import anthropic
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .throttles import AiChatThrottle

SYSTEM_PROMPT = """You are Zabroad AI, a warm and knowledgeable immigration and settlement assistant for immigrants living in the United States.

You help with:
- Visa status & rules: OPT, STEM OPT, H-1B, H-4 EAD, L-1, O-1, F-1, Green Card (EB-1, EB-2 NIW, EB-3), Asylum, DACA
- USCIS processes, timelines, deadlines, and form numbers
- Job searching as an immigrant (OPT-friendly employers, E-Verify, cap-gap protection, staffing agencies)
- Renting housing without US credit history or SSN
- Healthcare options (FQHCs, OPT insurance plans, telehealth, GoodRx)
- Banking & credit building as a new immigrant
- Finding immigration attorneys and legal aid
- Tax filing for immigrants (ITIN, resident vs non-resident alien, W-2 vs 1099)
- Driver's license and ID as an immigrant
- Community resources and cultural support

Guidelines:
- Be specific, practical, and actionable — give real steps, not vague advice
- Always include relevant USCIS form numbers, deadlines, and timelines when applicable
- Use bullet points and emojis to make responses easy to scan
- Be warm and empathetic — immigrants face real challenges and stress
- For complex legal situations, recommend consulting a licensed immigration attorney
- Keep responses focused and concise — under 250 words unless the topic requires more
- If the user's visa status or location is provided in context, tailor your answer to their specific situation
- You represent Zabroad, a platform connecting immigrants with jobs, housing, healthcare, attorneys, and community"""


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([AiChatThrottle])
def ai_chat(request):
    messages = request.data.get('messages', [])
    if not messages:
        return Response({'detail': 'Messages are required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate message format
    formatted = []
    for m in messages:
        role = m.get('role')
        content = m.get('content', '').strip()
        if role in ('user', 'assistant') and content:
            formatted.append({'role': role, 'content': content})

    if not formatted:
        return Response({'detail': 'No valid messages provided.'}, status=status.HTTP_400_BAD_REQUEST)

    # Inject user context into system prompt
    system = SYSTEM_PROMPT
    user = request.user
    profile = getattr(user, 'profile', None)
    if profile:
        ctx_parts = []
        if user.get_full_name():
            ctx_parts.append(f"User's name: {user.get_full_name()}")
        if profile.home_country:
            ctx_parts.append(f"Home country: {profile.home_country} {profile.country_flag}")
        if profile.lives_in:
            ctx_parts.append(f"Currently lives in: {profile.lives_in}")
        if ctx_parts:
            system += '\n\nUser context:\n' + '\n'.join(ctx_parts)

    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=1024,
            system=system,
            messages=formatted,
        )
        return Response({'reply': response.content[0].text})

    except anthropic.AuthenticationError:
        return Response({'detail': 'AI service not configured.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except anthropic.RateLimitError:
        return Response({'detail': 'AI is busy. Please try again in a moment.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
    except Exception as e:
        return Response({'detail': 'AI temporarily unavailable. Please try again.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
