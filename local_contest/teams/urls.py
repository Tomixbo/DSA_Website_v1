from django.urls import path
from . import views
from .views import (
    get_notifications, handle_join_request, join_team, list_teams,
    team_members, create_team, accept_request, reject_request
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
]
