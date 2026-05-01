import stripe
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

PLAN_AMOUNTS = {
    'standard': 499,   # $4.99 in cents
    'premium':  999,   # $9.99 in cents
}

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_intent(request):
    plan   = request.data.get('plan')
    amount = PLAN_AMOUNTS.get(plan)

    if not amount:
        return Response({'error': 'Invalid plan.'}, status=status.HTTP_400_BAD_REQUEST)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            metadata={'user_id': request.user.id, 'plan': plan},
        )
        return Response({
            'client_secret':   intent.client_secret,
            'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        })
    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
