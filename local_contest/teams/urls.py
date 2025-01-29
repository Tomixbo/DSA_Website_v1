from django.urls import path
from . import views
from .views import get_notifications, handle_join_request, join_team, list_teams, team_members

urlpatterns = [
    path('create/', views.create_team, name='create_team'),
    path('list/', list_teams, name='list_teams'),
    path('join/<int:team_id>/', join_team, name='join_team'),
    path('<int:team_id>/members/', team_members, name='team_members'),
    path('notifications/', get_notifications, name='get_notifications'),
    path('join_request/<int:request_id>/', handle_join_request, name='handle_join_request'),
    path('requests/accept/<int:request_id>/', views.accept_request, name='accept_request'),  # Vérifie cette ligne
    path('requests/reject/<int:request_id>/', views.reject_request, name='reject_request'),
]

