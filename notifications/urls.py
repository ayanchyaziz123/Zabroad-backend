from django.urls import path
from . import views

urlpatterns = [
    path('',                     views.NotificationListView.as_view(), name='notification_list'),
    path('unread-count/',        views.unread_count,                   name='unread_count'),
    path('mark-all-read/',       views.mark_all_read,                  name='mark_all_read'),
    path('delete-all/',          views.delete_all_notifications,       name='delete_all_notifications'),
    path('<int:pk>/read/',       views.mark_read,                      name='mark_read'),
    path('<int:pk>/delete/',     views.delete_notification,            name='delete_notification'),
]
