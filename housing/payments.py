import stripe
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from listings.models import Listing
from notifications.models import Notification
from accounts.models import Profile

stripe.api_key = settings.STRIPE_SECRET_KEY

PLAN_AMOUNTS = {
    'standard': 499,   # $4.99 in cents
    'premium':  999,   # $9.99 in cents
}


def _notify_nearby_users(listing, sender):
    """Bulk-create notifications for all users whose lives_in matches the listing's city."""
    city = listing.location.split(',')[0].strip() if listing.location else ''
    if not city:
        return

    nearby_profiles = (
        Profile.objects
        .filter(lives_in__icontains=city)
        .exclude(user=sender)
        .select_related('user')
    )

    notifications = [
        Notification(
            recipient=profile.user,
            sender=sender,
            type='housing',
            title='New housing near you 🏠',
            body=f'"{listing.title}" was just listed in {listing.location}. Tap to view.',
            post_id=listing.id,
        )
        for profile in nearby_profiles
    ]
    if notifications:
        Notification.objects.bulk_create(notifications, batch_size=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_intent(request):
    plan       = request.data.get('plan')
    listing_id = request.data.get('listing_id')
    amount     = PLAN_AMOUNTS.get(plan)

    if not amount:
        return Response({'detail': 'Invalid plan.'}, status=status.HTTP_400_BAD_REQUEST)

    if not listing_id:
        return Response({'detail': 'listing_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        Listing.objects.get(
            pk=listing_id,
            posted_by=request.user,
            listing_type=Listing.TYPE_HOUSING,
        )
    except Listing.DoesNotExist:
        return Response({'detail': 'Listing not found.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            metadata={
                'user_id':    request.user.id,
                'plan':       plan,
                'listing_id': listing_id,
            },
        )
        return Response({
            'client_secret':   intent.client_secret,
            'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        })
    except stripe.error.StripeError as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def notify_nearby(request):
    """Called after a premium listing is created to push notifications to nearby users."""
    listing_id = request.data.get('listing_id')
    if not listing_id:
        return Response({'detail': 'listing_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        listing = Listing.objects.get(
            pk=listing_id,
            posted_by=request.user,
            listing_type=Listing.TYPE_HOUSING,
            plan='premium',
        )
    except Listing.DoesNotExist:
        return Response({'detail': 'Premium listing not found.'}, status=status.HTTP_404_NOT_FOUND)

    city = listing.location.split(',')[0].strip() if listing.location else ''
    count = (
        Profile.objects
        .filter(lives_in__icontains=city)
        .exclude(user=request.user)
        .count()
    ) if city else 0

    _notify_nearby_users(listing, request.user)

    return Response({'detail': 'Notifications sent.', 'notified_count': count})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_premium_payment(request):
    payment_intent_id = request.data.get('payment_intent_id')
    listing_id        = request.data.get('listing_id')

    if not payment_intent_id or not listing_id:
        return Response(
            {'detail': 'payment_intent_id and listing_id are required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        listing = Listing.objects.select_related('posted_by').get(
            pk=listing_id,
            posted_by=request.user,
            listing_type=Listing.TYPE_HOUSING,
        )
    except Listing.DoesNotExist:
        return Response({'detail': 'Listing not found.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    except stripe.error.StripeError as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    if intent.status != 'succeeded':
        return Response({'detail': 'Payment not completed.'}, status=status.HTTP_400_BAD_REQUEST)

    # Ensure this intent belongs to the requesting user
    if str(intent.metadata.get('user_id')) != str(request.user.id):
        return Response({'detail': 'Payment does not match this account.'}, status=status.HTTP_403_FORBIDDEN)

    plan = intent.metadata.get('plan', 'standard')
    listing.plan = plan
    if plan == 'premium':
        listing.is_boosted = True
    listing.save(update_fields=['plan', 'is_boosted', 'updated_at'])

    if plan == 'premium':
        _notify_nearby_users(listing, request.user)

    return Response({'detail': f'Plan upgraded to {plan}.', 'plan': plan})
