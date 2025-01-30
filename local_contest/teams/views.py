from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from .models import JoinRequest, Team
from contest.models import Contest
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required
def list_teams(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)

    # ✅ Récupérer uniquement les équipes déjà inscrites à ce contest
    teams_in_contest = contest.teams.all()

    # ✅ Récupérer l'équipe de l'utilisateur dans CE contest
    user_team = teams_in_contest.filter(members=request.user).first()
    
    pending_requests = JoinRequest.objects.filter(user=request.user, team__in=teams_in_contest, status="pending")


    return render(request, 'teams/team_list.html', {
        'contest': contest,
        'teams': teams_in_contest,
        'user_team': user_team,
        'pending_requests': pending_requests
    })





@login_required
def create_team(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)

    if request.method == "POST":
        team_name = request.POST.get("name")

        # ✅ Vérifier si une équipe avec ce nom existe DANS TOUTE LA BASE DE DONNÉES
        if Team.objects.filter(name=team_name).exists():
            messages.error(request, "Ce nom de team existe déjà. Veuillez en choisir un autre.")
            return redirect('create_team', contest_id=contest.id)  # ✅ Retourne sur la page de création

        # ✅ Créer la team et ajouter l'utilisateur comme propriétaire et membre
        team = Team.objects.create(name=team_name, owner=request.user)
        team.members.add(request.user)

        # ✅ Associer l'équipe au contest
        contest.teams.add(team)

        messages.success(request, f"Votre équipe {team_name} a été créée avec succès !")
        return redirect('contest_detail', contest_id=contest.id)  # ✅ Redirige vers le contest

    return render(request, "teams/create_teams.html", {"contest": contest})


@login_required
def join_team(request, contest_id, team_id):
    contest = get_object_or_404(Contest, id=contest_id)
    team = get_object_or_404(Team, id=team_id, contests=contest)  # ✅ Vérifier que la team appartient bien au contest

    # ✅ Vérifier si l'utilisateur a déjà une team DANS CE CONTEST
    user_team = Team.objects.filter(members=request.user, contests=contest).first()
    
    if user_team:
        messages.error(request, "You are already in a team for this contest!")
        return redirect("list_teams", contest_id=contest.id)
    
    # Vérifier si l'utilisateur a déjà une demande en attente pour cette équipe
    existing_request = JoinRequest.objects.filter(user=request.user, team=team, status='pending').exists()
    if existing_request:
        messages.warning(request, "You have already sent a join request to this team!")
        return redirect('list_teams')
    
    # ✅ Vérifier si la team a de la place
    if team.members.count() >= 5:
        messages.error(request, "This team is already full!")
        return redirect("list_teams", contest_id=contest.id)

    # ✅ Créer une demande d'adhésion
    JoinRequest.objects.create(user=request.user, team=team)

    messages.success(request, f"Your request to join the team {team.name} has been sent!")
    return redirect("contest_inscription", contest_id=contest.id)

def team_members(request, contest_id, team_id):
    contest = get_object_or_404(Contest, id=contest_id)
    team = get_object_or_404(Team, id=team_id)

    # Vérifier si l'utilisateur est membre de l'équipe
    is_member = request.user in team.members.all()

    # Filtrer les demandes en attente pour cette équipe
    pending_requests = team.join_requests.filter(status='pending')

    context = {
        'contest': contest,  # ✅ Passer le contest en contexte
        'team': team,
        'is_member': is_member,
        'pending_requests': pending_requests,  # ✅ Passer les demandes en attente
    }
    return render(request, 'teams/team_members.html', context)


@login_required
def get_notifications(request):
    # ✅ Vérifier si l'utilisateur est propriétaire d'une équipe
    user_teams = Team.objects.filter(owner=request.user)

    # ✅ Récupérer les demandes d'adhésion en attente pour les équipes qu'il possède
    join_requests = JoinRequest.objects.filter(team__in=user_teams, status='pending').order_by('-created_at')

    # ✅ Transformer les demandes en format JSON
    data = {
        "notifications": [
            {
                "id": req.id,
                "message": f"{req.user.username} has requested to join {req.team.name}.",
                "created_at": req.created_at.strftime('%Y-%m-%d %H:%M')
            }
            for req in join_requests
        ]
    }
    return JsonResponse(data)

def handle_join_request(request, request_id):
    join_request = get_object_or_404(JoinRequest, id=request_id)

    # Vérifier si l'utilisateur est membre de l'équipe
    if request.user not in join_request.team.members.all():
        messages.error(request, "You are not allowed to manage this request!")
        return redirect('list_teams')

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "accept":
            join_request.accept()
            messages.success(request, f"{join_request.user.username} has been added to the team!")
        elif action == "reject":
            join_request.reject()
            messages.info(request, f"{join_request.user.username}'s request has been rejected.")

    return redirect('list_teams')

@login_required
def accept_request(request, request_id):
    join_request = get_object_or_404(JoinRequest, id=request_id)

    # ✅ Vérifie que la demande est toujours en attente
    if join_request.status != 'pending':
        messages.error(request, "This request has already been processed.")
        return redirect("list_teams", contest_id=join_request.team.contests.first().id)

    # ✅ Ajoute l'utilisateur à l'équipe et met à jour le statut
    join_request.accept()

    messages.success(request, f"{join_request.user.username} has been added to the team {join_request.team.name}.")

    # ✅ Récupère le contest_id en accédant aux contests liés à l'équipe
    contest_id = join_request.team.contests.first().id

    return redirect("team_members", contest_id=contest_id, team_id=join_request.team.id)


@login_required
def reject_request(request, request_id):
    join_request = get_object_or_404(JoinRequest, id=request_id)

    # Vérifie si l'utilisateur a les droits nécessaires pour rejeter la demande
    if join_request.team.owner == request.user:
        join_request.reject()
        messages.success(request, f"The request from {join_request.user.username} has been rejected.")
    else:
        messages.error(request, "You don't have permission to reject this request.")
    
    # ✅ Récupère le contest_id en accédant aux contests liés à l'équipe
    contest_id = join_request.team.contests.first().id

    return redirect("team_members", contest_id=contest_id, team_id=join_request.team.id)