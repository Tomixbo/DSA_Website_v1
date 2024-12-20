from django.urls import path
from . import views

urlpatterns = [
    path('create_post/', views.create_post, name='create_post'),
    path('', views.post_list, name='post_list'),
    path('create_post_ajax/', views.create_post_ajax, name='create_post_ajax'),

    path('post/like/<int:post_id>/', views.like_post, name='like_post'),
]