from django.urls import path
from . import views

urlpatterns = [
    path('',                                             views.ConversationListView.as_view(),  name='conversation_list'),
    path('start/',                                       views.get_or_create_conversation,      name='conversation_start'),
    path('<int:convo_id>/messages/',                     views.MessageListCreateView.as_view(), name='message_list'),
    path('<int:convo_id>/delete/',                       views.delete_conversation,             name='delete_conversation'),
    path('<int:convo_id>/messages/<int:msg_id>/delete/', views.delete_message,                  name='delete_message'),
]
