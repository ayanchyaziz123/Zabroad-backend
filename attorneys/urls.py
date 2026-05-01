from django.urls import path
from . import views
from .payments import create_payment_intent

urlpatterns = [
    path('',                views.AttorneyListCreateView.as_view(), name='attorney_list'),
    path('<int:pk>/',       views.AttorneyDetailView.as_view(),     name='attorney_detail'),
    path('payment-intent/', create_payment_intent,                  name='attorney_payment_intent'),
]
