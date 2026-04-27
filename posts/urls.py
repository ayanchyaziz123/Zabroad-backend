from django.urls import path
from . import views

urlpatterns = [
    path('',                     views.PostListCreateView.as_view(),   name='post_list'),
    path('<int:pk>/',            views.PostDetailView.as_view(),       name='post_detail'),
    path('<int:pk>/like/',       views.toggle_like,                    name='toggle_like'),
    path('<int:pk>/comments/',   views.CommentListCreateView.as_view(), name='comments'),
]
