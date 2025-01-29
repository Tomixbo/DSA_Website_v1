from django.urls import path
from . import views

urlpatterns = [
    path('competition/', views.competition_list, name='competition_list'),
    path('competition/<int:pk>/', views.competition_detail, name='competition_detail'),
    path('competition/<int:pk>/participate/', views.competition_participate, name='competition_participate'),
    path('competition/<int:pk>/time-left/', views.competition_time_left, name='competition_time_left'),
    path('competition/<int:pk>/challenges/', views.competition_challenges, name='competition_challenges'),
]