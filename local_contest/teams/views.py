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

    # Récupérer uniquement les équipes déjà inscrites à ce contest
    teams_in_contest = contest.teams.all()

    # Récupérer l'équipe de l'utilisateur dans CE contest
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

        # Check if the team name already exists
        if Team.objects.filter(name=team_name).exists():
            messages.error(request, "This team name already exists. Please choose another.")
            return redirect('create_team', contest_id=contest.id)  # Return to the creation page

        # Delete all pending join requests the user has sent
        JoinRequest.objects.filter(user=request.user, status='pending').delete()

        # Delete all pending invitations the user has received
        Invitation.objects.filter(user=request.user, status="pending").delete()

        # Create the team and add the user as owner and member
        team = Team.objects.create(name=team_name, owner=request.user)
        team.members.add(request.user)

        # Associate the team with the contest
        contest.teams.add(team)

        messages.success(request, f"Your team {team_name} has been created successfully!")
        return redirect('contest_detail', contest_id=contest.id)  # Redirect to contest detail

    return render(request, "teams/create_teams.html", {"contest": contest})




@login_required
def join_team(request, contest_id, team_id):
    contest = get_object_or_404(Contest, id=contest_id)
    team = get_object_or_404(Team, id=team_id, contests=contest)  # Vérifier que la team appartient bien au contest

    # Vérifier si l'utilisateur a déjà une team DANS CE CONTEST
    user_team = Team.objects.filter(members=request.user, contests=contest).first()
    
    if user_team:
        messages.error(request, "You are already in a team for this contest!")
        return redirect("list_teams", contest_id=contest.id)
    
    # Vérifier si l'utilisateur a déjà une demande en attente pour cette équipe
    existing_request = JoinRequest.objects.filter(user=request.user, team=team, status='pending').exists()
    if existing_request:
        messages.warning(request, "You have already sent a join request to this team!")
        return redirect('list_teams')
    
    # Vérifier si la team a de la place
    if team.members.count() >= contest.team_members_max:
        messages.error(request, "This team is already full!")
        return redirect("list_teams", contest_id=contest.id)

    # Créer une demande d'adhésion
    JoinRequest.objects.create(user=request.user, team=team)

    messages.success(request, f"Your request to join the team {team.name} has been sent!")
    return redirect("contest_inscription", contest_id=contest.id)

@login_required
def team_members(request, contest_id, team_id):
    contest = get_object_or_404(Contest, id=contest_id)
    team = get_object_or_404(Team, id=team_id)

    # Vérifier si l'utilisateur est membre de l'équipe
    is_member = request.user in team.members.all()

    # Filtrer les demandes en attente pour cette équipe
    pending_requests = team.join_requests.filter(status='pending')

    # Obtenir les utilisateurs qui sont déjà dans une équipe pour ce contest
    users_in_other_teams = CustomUser.objects.filter(
        teams__contests=contest
    ).exclude(id__in=team.members.values_list('id', flat=True)).distinct()

    # Recherche d'un utilisateur qui N'EST PAS déjà dans une autre équipe
    query = request.GET.get('search', '').strip()
    search_results = CustomUser.objects.exclude(id=request.user.id).filter(username__icontains=query)

    # Exclure les utilisateurs qui appartiennent déjà à d'autres équipes dans ce contest
    search_results = search_results.exclude(id__in=users_in_other_teams.values_list('id', flat=True))

    context = {
        'contest': contest,  
        'team': team,
        'is_member': is_member,
        'pending_requests': pending_requests,
        'search_results': search_results,  
        'query': query,
    }
    return render(request, 'teams/team_members.html', context)



@login_required
def get_notifications(request):
    # Vérifier si l'utilisateur est propriétaire d'une équipe
    user_teams = Team.objects.filter(owner=request.user)

    # Récupérer les demandes d'adhésion en attente pour les équipes qu'il possède
    join_requests = JoinRequest.objects.filter(team__in=user_teams, status='pending').order_by('-created_at')

    # Transformer les demandes en format JSON
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



@login_required
def accept_request(request, request_id):
    join_request = get_object_or_404(JoinRequest, id=request_id)

    # Check that the request is still pending
    if join_request.status != "pending":
        messages.error(request, "This request has already been processed.")
        return redirect("list_teams", contest_id=join_request.team.contests.first().id)
    
    # Vérifier si la team a de la place
    if join_request.team.members.count() >= join_request.team.contests.first().team_members_max:
        messages.error(request, "This team is already full!")
        return redirect("list_teams", contest_id=join_request.team.contests.first().id)

    # Add the user to the team and mark request as accepted
    join_request.accept()

    # Delete all other pending join requests for this team when team is full
    # Delete all other pending invitation made by this team
    if join_request.team.members.count() >= join_request.team.contests.first().team_members_max:
        JoinRequest.objects.filter(team=join_request.team, status="pending").delete()
        Invitation.objects.filter(team=join_request.team, status="pending").delete()
    

    # Retrieve contest_id for redirection
    contest_id = join_request.team.contests.first().id

    # Delete all pending invitations for this user
    Invitation.objects.filter(user=join_request.user, status="pending").delete()

    # Delete all other pending join requests made by this user
    JoinRequest.objects.filter(user=join_request.user, status="pending").delete()

    messages.success(request, f"{join_request.user.username} has been added to the team {join_request.team.name}.")

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
    
    # Récupère le contest_id en accédant aux contests liés à l'équipe
    contest_id = join_request.team.contests.first().id

    return redirect("team_members", contest_id=contest_id, team_id=join_request.team.id)

@login_required
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
def send_invitation(request, team_id, user_id):
    team = get_object_or_404(Team, id=team_id)
    invited_user = get_object_or_404(CustomUser, id=user_id)
    # Vérifier si l'utilisateur qui invite est bien membre ou propriétaire
    if request.user not in team.members.all() and request.user != team.owner:
        messages.warning(request, "You don't have the authorization to invite member!")
        return redirect("list_teams", contest_id=team.contests.first().id)
    # Vérifier si l'utilisateur est déjà dans l'équipe
    if invited_user in team.members.all():
        messages.warning(request, f"{invited_user.username} is already in your team!")
        return redirect("list_teams", contest_id=team.contests.first().id)
    # Vérifier si une invitation est déjà en attente
    if Invitation.objects.filter(user=invited_user, team=team, status='pending').exists():
        messages.warning(request, f"You have already sent an invitation to {invited_user.username}!")
        return redirect("list_teams", contest_id=team.contests.first().id)
    # Créer l'invitation
    invitation = Invitation.objects.create(user=invited_user, team=team, status="pending")
    # Créer une notification
    Notification.objects.create(
        user=invited_user,
        message=f"Vous avez reçu une invitation pour rejoindre l'équipe {team.name}.",
    )
    messages.success(request, f"Your invitation for {invited_user.username} to join your team has been sent!")
    return redirect("list_teams", contest_id=invitation.team.contests.first().id)

@login_required
def accept_invite(request, invite_id):
    invite = get_object_or_404(Invitation, id=invite_id, user=request.user, status="pending")
    team = invite.team

    # Vérifier si la team a de la place
    if team.members.count() >= invite.team.contests.first().team_members_max:
        messages.error(request, "This team is already full!")
        return redirect("list_teams", contest_id=invite.team.contests.first().id)
    
    # Add the user to the team
    invite.accept()

    # Delete all other pending join requests for this team when team is full
    # Delete all other pending invitation made by this team
    if invite.team.members.count() >= invite.team.contests.first().team_members_max:
        JoinRequest.objects.filter(team=invite.team, status="pending").delete()
        Invitation.objects.filter(team=invite.team, status="pending").delete()

    # Get the contest_id associated with the team
    contest_id = invite.team.contests.first().id

    # Delete all other pending invitations for this user
    Invitation.objects.filter(user=request.user, status="pending").exclude(id=invite.id).delete()

    # Delete all join requests the user has previously made
    JoinRequest.objects.filter(user=request.user, status="pending").delete()

    messages.success(request, f"You have joined the team '{team.name}'!")
    
    return redirect("team_members", contest_id=contest_id, team_id=team.id)


@login_required
def decline_invite(request, invite_id):
    invite = get_object_or_404(Invitation, id=invite_id)
    invite.delete()  # Supprime l'invitation après refus
    # Récupère le contest_id en accédant aux contests liés à l'équipe
    contest_id = invite.team.contests.first().id

    return redirect("team_members", contest_id=contest_id, team_id=invite.team.id)