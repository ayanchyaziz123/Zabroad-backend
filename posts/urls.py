from django.urls import path
from . import views

urlpatterns = [
    path('',                     views.PostListCreateView.as_view(),   name='post_list'),
    path('saved/',               views.saved_posts,                    name='saved_posts'),
    path('<int:pk>/',            views.PostDetailView.as_view(),       name='post_detail'),
    path('<int:pk>/like/',       views.toggle_like,                    name='toggle_like'),
    path('<int:pk>/save/',       views.toggle_save,                    name='toggle_save'),
    path('<int:pk>/comments/',   views.CommentListCreateView.as_view(), name='comments'),
]
