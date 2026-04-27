from django.urls import path
from . import views

urlpatterns = [
    path('',                views.EventListCreateView.as_view(),  name='event_list'),
    path('<int:pk>/',       views.EventDetailView.as_view(),      name='event_detail'),
    path('<int:pk>/rsvp/',  views.rsvp_event,                    name='rsvp_event'),
]
