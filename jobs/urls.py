from django.urls import path
from . import views
from .payments import create_payment_intent

urlpatterns = [
    path('',                  views.JobListCreateView.as_view(), name='job_list'),
    path('<int:pk>/',         views.JobDetailView.as_view(),     name='job_detail'),
    path('payment-intent/',   create_payment_intent,             name='job_payment_intent'),
]
