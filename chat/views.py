from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class ConversationListView(generics.ListAPIView):
    """List all conversations for the logged-in user."""
    serializer_class   = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def get_queryset(self):
        return (
            Conversation.objects
            .filter(participants=self.request.user)
            .prefetch_related('participants', 'messages')
            .distinct()
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def get_or_create_conversation(request):
    """Get or create a 1-to-1 conversation with another user."""
    other_id = request.data.get('user_id')
    if not other_id:
        return Response({'error': 'user_id required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        other = User.objects.get(id=other_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Find existing 1-to-1 conversation between these two users
    convo = (
        Conversation.objects
        .filter(participants=request.user)
        .filter(participants=other)
        .first()
    )

    if not convo:
        convo = Conversation.objects.create()
        convo.participants.add(request.user, other)

    serializer = ConversationSerializer(convo, context={'request': request})
    return Response(serializer.data)


class MessageListCreateView(generics.ListCreateAPIView):
    """List and send messages in a conversation."""
    serializer_class   = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def get_queryset(self):
        convo_id = self.kwargs['convo_id']
        # Mark incoming messages as read
        Message.objects.filter(
            conversation_id=convo_id,
            is_read=False,
        ).exclude(sender=self.request.user).update(is_read=True)
        return Message.objects.filter(conversation_id=convo_id)

    def perform_create(self, serializer):
        convo_id = self.kwargs['convo_id']
        try:
            convo = Conversation.objects.get(id=convo_id, participants=self.request.user)
        except Conversation.DoesNotExist:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied()
        serializer.save(sender=self.request.user, conversation=convo)
