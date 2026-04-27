from django.urls import path
from . import views

urlpatterns = [
    path('',          views.HousingListCreateView.as_view(),  name='housing_list'),
    path('<int:pk>/', views.HousingDetailView.as_view(),      name='housing_detail'),
]
