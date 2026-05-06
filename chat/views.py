from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Conversation
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
        # Verify the requesting user is a participant — prevents ID-guessing attacks
        try:
            convo = Conversation.objects.get(id=convo_id, participants=self.request.user)
        except Conversation.DoesNotExist:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied()
        # Mark incoming messages as read
        convo.messages.filter(is_read=False).exclude(sender=self.request.user).update(is_read=True)
        return convo.messages.all()

    def perform_create(self, serializer):
        convo_id = self.kwargs['convo_id']
        try:
            convo = Conversation.objects.get(id=convo_id, participants=self.request.user)
        except Conversation.DoesNotExist:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied()
        serializer.save(sender=self.request.user, conversation=convo)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_conversation(request, convo_id):
    deleted, _ = Conversation.objects.filter(id=convo_id, participants=request.user).delete()
    if not deleted:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_message(request, convo_id, msg_id):
    from .models import Message
    try:
        msg = Message.objects.get(id=msg_id, conversation__id=convo_id, sender=request.user)
    except Message.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    msg.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
