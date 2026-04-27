from django.urls import path
from . import views

urlpatterns = [
    path('',          views.AttorneyListCreateView.as_view(),  name='attorney_list'),
    path('<int:pk>/', views.AttorneyDetailView.as_view(),      name='attorney_detail'),
]
