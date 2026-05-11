from django.urls import path
from . import views
from .payments import create_payment_intent, confirm_premium_payment, notify_nearby

urlpatterns = [
    path('',                  views.HousingListCreateView.as_view(), name='housing_list'),
    path('<int:pk>/',         views.HousingDetailView.as_view(),     name='housing_detail'),
    path('payment-intent/',   create_payment_intent,                 name='housing_payment_intent'),
    path('confirm-payment/',  confirm_premium_payment,               name='housing_confirm_payment'),
    path('notify-nearby/',    notify_nearby,                         name='housing_notify_nearby'),
]
