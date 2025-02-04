from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from .models import JoinRequest, Team
from contest.models import Contest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from members.models import CustomUser
from .models import Invitation, JoinRequest, Notification, Team

@login_required
def list_teams(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)

    # ✅ Récupérer uniquement les équipes déjà inscrites à ce contest
    teams_in_contest = contest.teams.all()

    # ✅ Récupérer l'équipe de l'utilisateur dans CE contest
    user_team = teams_in_contest.filter(members=request.user).first()
    
    pending_requests = JoinRequest.objects.filter(user=request.user, team__in=teams_in_contest, status="pending")
    
    pending_invitations = Invitation.objects.filter(user=request.user, status="pending")


    return render(request, 'teams/team_list.html', {
        'contest': contest,
        'teams': teams_in_contest,
        'user_team': user_team,
        'pending_requests': pending_requests,
        "pending_invitations": pending_invitations,
    })





@login_required
def create_team(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)

    if request.method == "POST":
        team_name = request.POST.get("name")

        # ✅ Vérifier si une équipe avec ce nom existe DANS TOUTE LA BASE DE DONNÉES
        if Team.objects.filter(name=team_name).exists():
            messages.error(request, "This team name already exists. Please choose another.")
            return redirect('create_team', contest_id=contest.id)  # ✅ Retourne sur la page de création

        # ✅ Supprimer toutes les demandes d'adhésion en attente de cet utilisateur avant de créer l'équipe
        JoinRequest.objects.filter(user=request.user, status='pending').delete()

        # ✅ Créer la team et ajouter l'utilisateur comme propriétaire et membre
        team = Team.objects.create(name=team_name, owner=request.user)
        team.members.add(request.user)

        # ✅ Associer l'équipe au contest
        contest.teams.add(team)

        messages.success(request, f"Your team {team_name} has been created successfully!")
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

        # Recherche d'un utilisateur
    query = request.GET.get('search', '')
    search_results = CustomUser.objects.exclude(id=request.user.id).filter(username__icontains=query)

    context = {
        'contest': contest,  # ✅ Passer le contest en contexte
        'team': team,
        'is_member': is_member,
        'pending_requests': pending_requests,
        'search_results': search_results,  # Ajout des résultats de recherche au contexte
        'query': query,  # Passer la requête de recherche pour la barre de recherche
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

# invitation
def send_join_request(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    # Vérifier si l'utilisateur fait déjà partie d'une équipe
    user_team = Team.objects.filter(members=request.user).first()
    
    if user_team:
        messages.error(request, "You are already in a team!")
        return redirect('list_teams')
    # Vérifier si l'utilisateur a déjà une demande en attente pour cette équipe
    existing_request = JoinRequest.objects.filter(user=request.user, team=team, status='pending').exists()
    if existing_request:
        messages.warning(request, "You have already sent a join request to this team!")
        return redirect('list_teams')
    # Créer une demande d'adhésion
    JoinRequest.objects.create(user=request.user, team=team)
    messages.success(request, f"Your request to join the team {team.name} has been sent!")
    
    return redirect('team_members', team_id=team.id)
@login_required
def send_invite_request(request, team_id, user_id):
    team = get_object_or_404(Team, id=team_id)
    user_to_invite = get_object_or_404(CustomUser, id=user_id)
    # Vérifier si l'utilisateur fait déjà partie de l'équipe
    if user_to_invite in team.members.all():
        return JsonResponse({"status": "error", "message": "User is already in the team!"}, status=400)
    # Vérifier si une demande est déjà en attente
    existing_request = JoinRequest.objects.filter(user=user_to_invite, team=team, status='pending').exists()
    if existing_request:
        return JsonResponse({"status": "error", "message": "Request already sent!"}, status=400)
    # Créer la demande d'adhésion
    JoinRequest.objects.create(user=user_to_invite, team=team)
    return JsonResponse({"status": "success", "message": "Invitation sent!"})
@login_required
def accept_invite(request, invite_id):
    invite = get_object_or_404(Invitation, id=invite_id, user=request.user, status="pending")
    team = invite.team
    # Ajouter l'utilisateur à l'équipe
    team.members.add(request.user)
    invite.status = "accepted"
    invite.save()
    # ✅ Récupère le contest_id en accédant aux contests liés à l'équipe
    contest_id = invite.team.contests.first().id

    return redirect("team_members", contest_id=contest_id, team_id=invite.team.id)
@login_required
def send_invitation(request, team_id, user_id):
    team = get_object_or_404(Team, id=team_id)
    invited_user = get_object_or_404(CustomUser, id=user_id)
    # Vérifier si l'utilisateur qui invite est bien membre ou propriétaire
    if request.user not in team.members.all() and request.user != team.owner:
        return JsonResponse({"error": "Vous n'avez pas l'autorisation d'inviter quelqu'un"}, status=403)
    # Vérifier si l'utilisateur est déjà dans l'équipe
    if invited_user in team.members.all():
        return JsonResponse({"error": "Cet utilisateur est déjà membre de l'équipe"}, status=400)
    # Vérifier si une invitation est déjà en attente
    if Invitation.objects.filter(user=invited_user, team=team, status='pending').exists():
        return JsonResponse({"error": "Une invitation est déjà en attente"}, status=400)
    # Créer l'invitation
    invitation = Invitation.objects.create(user=invited_user, team=team, status="pending")
    # Créer une notification
    Notification.objects.create(
        user=invited_user,
        message=f"Vous avez reçu une invitation pour rejoindre l'équipe {team.name}.",
    )
    return redirect("list_teams", contest_id=invitation.team.contests.first().id)
@login_required
def respond_to_invitation(request, invitation_id, response):
    invitation = get_object_or_404(Invitation, id=invitation_id)
    # Vérifier si l'utilisateur est bien l'invité
    if request.user != invitation.user:
        return JsonResponse({"error": "Vous ne pouvez pas répondre à cette invitation"}, status=403)
    if response == 'accept':
        invitation.status = "accepted"
        invitation.team.members.add(invitation.user)
        message = f"{request.user.username} a accepté l'invitation pour rejoindre l'équipe {invitation.team.name}."
    elif response == 'reject':
        invitation.status = "rejected"
        message = f"{request.user.username} a refusé l'invitation pour rejoindre l'équipe {invitation.team.name}."
    else:
        return JsonResponse({"error": "Réponse invalide"}, status=400)
    invitation.save()
    # Envoyer une notification au propriétaire de l'équipe
    Notification.objects.create(
        user=invitation.team.owner,
        message=message
    )
    return redirect('team_list')  # Rediriger vers la liste des équipes
def decline_invite(request, invite_id):
    invite = get_object_or_404(Invitation, id=invite_id)
    invite.delete()  # Supprime l'invitation après refus
    # ✅ Récupère le contest_id en accédant aux contests liés à l'équipe
    contest_id = invite.team.contests.first().id

    return redirect("team_members", contest_id=contest_id, team_id=invite.team.id)