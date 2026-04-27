from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import OTPVerification
from .serializers import RegisterSerializer, UserSerializer, ProfileSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def send_otp(request):
    email = request.data.get('email', '').strip().lower()
    if not email or '@' not in email:
        return Response({'detail': 'Valid email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({'detail': 'This email is already registered. Please log in instead.'}, status=status.HTTP_400_BAD_REQUEST)

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

    otp = OTPVerification.objects.filter(email=email, code=code, is_used=False).order_by('-created_at').first()

    if not otp:
        return Response({'detail': 'Invalid verification code.'}, status=status.HTTP_400_BAD_REQUEST)
    if otp.is_expired():
        return Response({'detail': 'Code has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)

    otp.is_used = True
    otp.save(update_fields=['is_used'])
    return Response({'detail': 'Email verified.', 'verified': True})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
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
def logout(request):
    try:
        token = RefreshToken(request.data.get('refresh'))
        token.blacklist()
    except (TokenError, Exception):
        pass
    return Response({'detail': 'Logged out.'}, status=status.HTTP_200_OK)


@api_view(['GET', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    user = request.user
    if request.method == 'GET':
        return Response(UserSerializer(user).data)

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
    profile_serializer = ProfileSerializer(user.profile, data=request.data, partial=True)
    if profile_serializer.is_valid():
        profile_serializer.save()
        user.refresh_from_db()
        return Response(UserSerializer(user).data)
    return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
