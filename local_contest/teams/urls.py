from django.urls import path
from .views import (
    get_notifications, handle_join_request, join_team, list_teams,
    team_members, create_team, accept_request, reject_request, send_invitation, accept_invite, decline_invite, respond_to_invitation
)

urlpatterns = [
    # ✅ Liste des équipes d'un contest spécifique
    path('<int:contest_id>/list_team/', list_teams, name='list_teams'),

    # ✅ Création d'une équipe pour un contest spécifique
    path('<int:contest_id>/teams/create/', create_team, name='create_team'),

    # ✅ Rejoindre une équipe dans un contest spécifique
    path('<int:contest_id>/teams/<int:team_id>/join/', join_team, name='join_team'),

    # ✅ Voir les membres d'une équipe spécifique dans un contest
    path('<int:contest_id>/teams/<int:team_id>/members/', team_members, name='team_members'),

    # ✅ Notifications liées aux demandes d'équipe
    path('notifications/', get_notifications, name='get_notifications'),

    # ✅ Gérer une demande d'adhésion à une équipe
    path('join_request/<int:request_id>/', handle_join_request, name='handle_join_request'),

    # ✅ Accepter ou rejeter une demande d'adhésion
    path('requests/accept/<int:request_id>/', accept_request, name='accept_request'),
    path('requests/reject/<int:request_id>/', reject_request, name='reject_request'),
    path('join_request/<int:request_id>/', handle_join_request, name='handle_join_request'),  # Vérifie cette ligne
    path('teams/<int:team_id>/invite/<int:user_id>/', send_invitation, name='send_invite'),
    path('teams/accept_invite/<int:invite_id>/', accept_invite, name='accept_invite'),
    path('teams/decline_invite/<int:invite_id>/', decline_invite, name='decline_invite'),
    path('invitations/<int:invitation_id>/<str:response>/', respond_to_invitation, name='respond_invite'),
    path('teams/accept_request/<int:request_id>/', accept_request, name='accept_request'),
]
