from django.urls import path
from . import views

urlpatterns = [
    path('',          views.MarketplaceListCreateView.as_view(), name='marketplace_list'),
    path('<int:pk>/', views.MarketplaceDetailView.as_view(),     name='marketplace_detail'),
]
