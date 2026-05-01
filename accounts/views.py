import hmac
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import OTPVerification
from .serializers import RegisterSerializer, UserSerializer, ProfileSerializer

OTP_RATE_LIMIT_SECONDS = 60  # minimum gap between OTP sends per email


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def send_otp(request):
    email = request.data.get('email', '').strip().lower()
    if not email or '@' not in email:
        return Response({'detail': 'Valid email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({'detail': 'This email is already registered. Please log in instead.'}, status=status.HTTP_400_BAD_REQUEST)

    # Rate limit: block if a fresh OTP was sent within the cooldown window
    recent = OTPVerification.objects.filter(email=email).order_by('-created_at').first()
    if recent:
        seconds_since = (timezone.now() - recent.created_at).total_seconds()
        if seconds_since < OTP_RATE_LIMIT_SECONDS:
            wait = int(OTP_RATE_LIMIT_SECONDS - seconds_since)
            return Response(
                {'detail': f'Please wait {wait} seconds before requesting a new code.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

    otp = OTPVerification.generate(email)

    send_mail(
        subject='Your Zabroad verification code',
        message=(
            f'Your Zabroad verification code is: {otp.code}\n\n'
            f'This code expires in 10 minutes. Do not share it with anyone.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
    return Response({'detail': 'OTP sent.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_otp(request):
    email = request.data.get('email', '').strip().lower()
    code  = request.data.get('code', '').strip()

    if not email or not code:
        return Response({'detail': 'Email and code are required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Find the latest unused OTP for this email (don't filter by code yet — need brute-force check)
    otp = OTPVerification.objects.filter(email=email, is_used=False).order_by('-created_at').first()

    if not otp:
        return Response({'detail': 'No active code found. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)
    if otp.is_expired():
        return Response({'detail': 'Code has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)
    if otp.is_locked():
        return Response({'detail': 'Too many incorrect attempts. Please request a new code.'}, status=status.HTTP_400_BAD_REQUEST)

    # Use constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(otp.code, code):
        otp.attempts += 1
        otp.save(update_fields=['attempts'])
        remaining = OTPVerification.MAX_ATTEMPTS - otp.attempts
        if remaining <= 0:
            return Response({'detail': 'Too many incorrect attempts. Please request a new code.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {'detail': f'Invalid code. {remaining} attempt{"s" if remaining != 1 else ""} remaining.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    otp.is_used    = True
    otp.verified_at = timezone.now()
    otp.save(update_fields=['is_used', 'verified_at'])
    return Response({'detail': 'Email verified.', 'verified': True})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    email = request.data.get('email', '').strip().lower()

    # Require a successfully verified OTP for this email within the last 15 minutes
    cutoff = timezone.now() - timedelta(minutes=15)
    email_verified = OTPVerification.objects.filter(
        email=email,
        is_used=True,
        verified_at__isnull=False,
        verified_at__gte=cutoff,
    ).exists()
    if not email_verified:
        return Response(
            {'detail': 'Email not verified. Please complete OTP verification first.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'user':    UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def forgot_password(request):
    """Send a password-reset OTP to the given email (only if account exists)."""
    email = request.data.get('email', '').strip().lower()
    if not email or '@' not in email:
        return Response({'detail': 'Valid email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Always return the same message to avoid email enumeration.
    # Silently enforce rate limit and account existence check.
    if User.objects.filter(email=email).exists():
        recent = OTPVerification.objects.filter(email=email).order_by('-created_at').first()
        too_soon = recent and (timezone.now() - recent.created_at).total_seconds() < OTP_RATE_LIMIT_SECONDS
        if not too_soon:
            otp = OTPVerification.generate(email)
            send_mail(
                subject='Reset your Zabroad password',
                message=(
                    f'Your Zabroad password-reset code is: {otp.code}\n\n'
                    f'This code expires in 10 minutes. If you did not request this, ignore this email.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
    return Response({'detail': 'If an account exists for that email, a reset code has been sent.'})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def reset_password(request):
    """Verify OTP and set a new password."""
    email    = request.data.get('email', '').strip().lower()
    code     = request.data.get('code', '').strip()
    password = request.data.get('password', '')

    if not email or not code or not password:
        return Response({'detail': 'Email, code, and new password are required.'}, status=status.HTTP_400_BAD_REQUEST)
    if len(password) < 8:
        return Response({'detail': 'Password must be at least 8 characters.'}, status=status.HTTP_400_BAD_REQUEST)

    otp = OTPVerification.objects.filter(email=email, is_used=False).order_by('-created_at').first()
    if not otp:
        return Response({'detail': 'Invalid or expired code.'}, status=status.HTTP_400_BAD_REQUEST)
    if otp.is_expired():
        return Response({'detail': 'Code has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)
    if otp.is_locked():
        return Response({'detail': 'Too many incorrect attempts. Please request a new code.'}, status=status.HTTP_400_BAD_REQUEST)

    if not hmac.compare_digest(otp.code, code):
        otp.attempts += 1
        otp.save(update_fields=['attempts'])
        return Response({'detail': 'Invalid code.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'detail': 'No account found for this email.'}, status=status.HTTP_404_NOT_FOUND)

    # Run Django's built-in password validators
    try:
        validate_password(password, user=user)
    except DjangoValidationError as e:
        return Response({'detail': ' '.join(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(password)
    user.save()
    otp.is_used = True
    otp.save(update_fields=['is_used'])
    return Response({'detail': 'Password reset successfully. Please sign in.'})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def logout(request):
    try:
        token = RefreshToken(request.data.get('refresh'))
        token.blacklist()
    except (TokenError, Exception):
        pass
    return Response({'detail': 'Logged out.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def public_profile(request, user_id):
    """Get any user's public profile + their posts."""
    try:
        target = User.objects.select_related('profile').get(pk=user_id)
    except User.DoesNotExist:
        return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    from posts.serializers import PostSerializer
    from posts.models import Post

    posts = Post.objects.filter(
        author=target, is_anonymous=False
    ).select_related('author__profile').prefetch_related('topics', 'likes', 'comments').order_by('-created_at')

    return Response({
        'user':  UserSerializer(target, context={'request': request}).data,
        'posts': PostSerializer(posts, many=True, context={'request': request}).data,
    })


@api_view(['GET', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    user = request.user
    if request.method == 'GET':
        return Response(UserSerializer(user, context={'request': request}).data)

    # Update top-level User fields
    user_fields = {}
    if 'first_name' in request.data:
        user_fields['first_name'] = request.data['first_name']
    if 'last_name' in request.data:
        user_fields['last_name'] = request.data['last_name']
    if user_fields:
        for field, value in user_fields.items():
            setattr(user, field, value)
        user.save(update_fields=list(user_fields.keys()))

    # Update Profile fields
    profile_serializer = ProfileSerializer(user.profile, data=request.data, partial=True, context={'request': request})
    if profile_serializer.is_valid():
        profile_serializer.save()
        user.refresh_from_db()
        return Response(UserSerializer(user, context={'request': request}).data)
    return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
