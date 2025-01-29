from django.urls import path

from teams.views import list_teams
from .views import contest_list, contest_detail, contest_challenge_detail, contest_inscription, contest_participate

urlpatterns = [
    path('contest-list/', contest_list, name='contest_list'),
    path('<int:contest_id>/', contest_detail, name='contest_detail'),
    path('<int:contest_id>/<str:challenge_slug>/', contest_challenge_detail, name='contest_challenge_detail'),
    path('inscription/<int:contest_id>/', contest_inscription, name='contest_inscription'),
    path('participate/<int:contest_id>/', contest_participate, name='contest_participate'),
    path('list/', list_teams, name='list_team'),

]
