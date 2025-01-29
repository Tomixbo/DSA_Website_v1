from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from .models import JoinRequest, Notification, Team
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def list_teams(request):
    teams = Team.objects.all()
    user_team = Team.objects.filter(members=request.user).first()  # Récupère l'équipe de l'utilisateur courant

    # Récupérer les IDs des équipes pour lesquelles l'utilisateur a déjà une demande en attente
    pending_requests = Team.objects.filter(join_requests__user=request.user, join_requests__status='pending')

    return render(request, 'teams/team_list.html', {
        'teams': teams,
        'user_team': user_team,
        'pending_requests': pending_requests,  # Ajouter les requêtes en attente au contexte
    })

def create_team(request):
    if request.method == "POST":
        team_name = request.POST.get("name")  # Récupérer le nom de la team

        # Vérifier si une team avec ce nom existe déjà
        if Team.objects.filter(name=team_name).exists():
            return render(request, "teams/create_teams.html", {"error": "Ce nom de team existe déjà."})

        # Créer la team et ajouter l'utilisateur comme propriétaire et membre
        team = Team.objects.create(name=team_name, owner=request.user)
        team.members.add(request.user)

        return redirect("/teams/list", team_id=team.id)  # Rediriger vers la page de la team

    return render(request, "teams/create_teams.html")

def join_team(request, team_id):
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

    # Vérifier si l'équipe a encore de la place
    if team.members.count() >= 5:
        messages.error(request, "This team is already full!")
        return redirect('list_teams')

    # Créer une demande d'adhésion
    JoinRequest.objects.create(user=request.user, team=team)
    messages.success(request, f"Your request to join the team {team.name} has been sent!")
    
    return redirect('list_teams')

def team_members(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    is_member = request.user in team.members.all()

    # Filtrer les demandes en attente dans la vue
    pending_requests = team.join_requests.filter(status='pending')

    context = {
        'team': team,
        'is_member': is_member,
        'pending_requests': pending_requests,  # Passer les demandes en attente au template
    }
    return render(request, 'teams/team_members.html', context)

def get_notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    data = {
        "notifications": [
            {
                "id": notif.id,
                "message": notif.message,
                "created_at": notif.created_at.strftime('%Y-%m-%d %H:%M')
            }
            for notif in notifications
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

    # Vérifie si l'utilisateur a les droits nécessaires pour accepter la demande
    if join_request.team.owner == request.user:
        join_request.accept()
        messages.success(request, f"{join_request.user.username} has been added to the team.")
    else:
        messages.error(request, "You don't have permission to accept this request.")
    
    return redirect('team_members', team_id=join_request.team.id)

@login_required
def reject_request(request, request_id):
    join_request = get_object_or_404(JoinRequest, id=request_id)

    # Vérifie si l'utilisateur a les droits nécessaires pour rejeter la demande
    if join_request.team.owner == request.user:
        join_request.reject()
        messages.success(request, f"The request from {join_request.user.username} has been rejected.")
    else:
        messages.error(request, "You don't have permission to reject this request.")
    
    return redirect('team_members', team_id=join_request.team.id)