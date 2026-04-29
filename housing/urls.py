from django.urls import path
from . import views
from .payments import create_payment_intent

urlpatterns = [
    path('',                views.HousingListCreateView.as_view(), name='housing_list'),
    path('<int:pk>/',       views.HousingDetailView.as_view(),     name='housing_detail'),
    path('payment-intent/', create_payment_intent,                 name='housing_payment_intent'),
]
