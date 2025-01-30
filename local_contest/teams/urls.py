from django.urls import path
from . import views
from .views import accept_invite, accept_request, decline_invite, get_notifications, handle_join_request, join_team, list_teams, respond_to_invitation, send_invitation, team_members

urlpatterns = [
    path('create/', views.create_team, name='create_team'),
    path('list/', list_teams, name='list_teams'),
    path('join/<int:team_id>/', join_team, name='join_team'),
    path('<int:team_id>/members/', team_members, name='team_members'),
    path('notifications/', get_notifications, name='get_notifications'),
    path('join_request/<int:request_id>/', handle_join_request, name='handle_join_request'),  # Vérifie cette ligne
    path('requests/reject/<int:request_id>/', views.reject_request, name='reject_request'),
    path('teams/<int:team_id>/invite/<int:user_id>/', send_invitation, name='send_invite'),
    path('teams/accept_invite/<int:invite_id>/', accept_invite, name='accept_invite'),
    path('teams/decline_invite/<int:invite_id>/', decline_invite, name='decline_invite'),
    path('invitations/<int:invitation_id>/<str:response>/', respond_to_invitation, name='respond_invite'),
    path('teams/accept_request/<int:request_id>/', accept_request, name='accept_request'),
]

