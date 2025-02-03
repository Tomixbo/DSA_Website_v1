from django.urls import path
from . import views

urlpatterns = [

    path('', views.post_list, name='post_list'),
    path('create_post_ajax/', views.create_post_ajax, name='create_post_ajax'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('post/like/<int:post_id>/', views.like_post, name='like_post'),
]