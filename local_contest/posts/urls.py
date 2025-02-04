from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('pin/<int:post_id>/', views.pin_post, name='pin_post'),
    path('unpin/', views.unpin_post, name='unpin_post'),
]