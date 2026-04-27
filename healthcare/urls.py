from django.urls import path
from . import views

urlpatterns = [
    path('',          views.DoctorListCreateView.as_view(),  name='doctor_list'),
    path('<int:pk>/', views.DoctorDetailView.as_view(),      name='doctor_detail'),
]
