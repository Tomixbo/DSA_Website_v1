from django.shortcuts import render, get_object_or_404, redirect
from .models import Contest
from teams.models import Team
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from challenges.models import Challenge, Level, DefinedFile, Performance
from django.db.models import Count, Q, OuterRef, Subquery
from django.utils import timezone
from django.db.models import Max


from django.db.models import Max
from django.utils.timezone import make_aware

@login_required
def contest_leaderboard(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    teams = contest.teams.all()
    user = request.user
    user_team = contest.teams.filter(members=user).first()

    leaderboard_data = []

    # Récupérer toutes les defined_files du contest
    total_defined_files = DefinedFile.objects.filter(
        level__challenge__contest_challenges__contest=contest
    ).count() or 1  # Évite division par 0

    # Définir la période valide du contest
    contest_start = contest.start_date
    contest_end = contest.end_date

    for team in teams:
        # Nombre de fichiers résolus par cette équipe dans la période du contest
        solved_files = Performance.objects.filter(
            definedfile__level__challenge__contest_challenges__contest=contest,
            user__in=team.members.all(),
            solved=True,
            created_at__range=(contest_start, contest_end)
        ).values("definedfile").distinct().count()

        # Dernière soumission de l'équipe dans la période du contest
        last_performance = Performance.objects.filter(
            user__in=team.members.all(),
            solved=True,
            created_at__range=(contest_start, contest_end)
        ).aggregate(last=Max("created_at"))["last"] or contest_start  # Evite None en mettant start_date du contest

        # Calcul du score
        score = (solved_files / total_defined_files) * 100

        leaderboard_data.append({
            "team": team,
            "score": round(score, 2),
            "last_performance": last_performance
        })

    # Trier par score DESC et dernière soumission ASC (plus rapide = meilleur classement)
    leaderboard_data.sort(key=lambda x: (-x["score"], x["last_performance"]))

    # Assignation des rangs stricts
    for index, entry in enumerate(leaderboard_data):
        entry["rank"] = index + 1  # Chaque team a un rank unique

    return render(request, 'contest/leaderboard.html', {
        "contest": contest,
        "leaderboard_data": leaderboard_data,
        "user_team": user_team,
    })




@login_required
def contest_list(request):
    contests = Contest.objects.all().order_by('-start_date')
    return render(request, 'contest/contest_list.html', {'contests': contests})



@login_required
def contest_detail(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    user = request.user

    # Vérifie si le contest est terminé
    if contest.is_finished():
        return redirect('contest_inscription', contest_id=contest.id)

    # Vérifie si l'utilisateur appartient à une équipe inscrite dans ce contest
    user_team = contest.teams.filter(members=user).first()  # Récupération correcte de l'équipe

    if not user_team:
        return redirect('contest_inscription', contest_id=contest.id)

    # Définir la période valide du contest
    contest_start = contest.start_date
    contest_end = contest.end_date
    
    # Récupération des challenges associés au contest
    challenges = Challenge.objects.filter(contest_challenges__contest=contest).order_by('category', 'name')

    # Compute total defined files per challenge
    defined_files_count = Challenge.objects.filter(
        pk=OuterRef('pk')
    ).annotate(
        count=Count('levels__defined_files')
    ).values('count')

    # Compute resolved files count (by team, within contest period)
    resolved_files_count = Challenge.objects.filter(
        pk=OuterRef('pk')
    ).annotate(
        count=Count(
            'levels__defined_files',
            filter=Q(
                levels__defined_files__performance__user__teams=user_team,
                levels__defined_files__performance__solved=True,
                levels__defined_files__performance__created_at__range=(contest_start, contest_end)
            )
        )
    ).values('count')

    # Annotate challenges with computed fields
    challenges = challenges.annotate(
        num_defined_files=Subquery(defined_files_count),
        num_resolved_defined_files=Subquery(resolved_files_count)
    )


    # Récupérer toutes les defined_files du contest
    total_defined_files = DefinedFile.objects.filter(
        level__challenge__contest_challenges__contest=contest
    ).count() or 1  # Évite division par 0

    


    # Nombre de fichiers résolus par cette équipe dans la période du contest
    solved_files = Performance.objects.filter(
        definedfile__level__challenge__contest_challenges__contest=contest,
        user__in=user_team.members.all(),
        solved=True,
        created_at__range=(contest_start, contest_end)
    ).values("definedfile").distinct().count()


    # Calcul du score
    progress_percent = (solved_files / total_defined_files) * 100

    return render(request, 'contest/contest_detail.html', {
        'contest': contest,
        'challenges': challenges,
        'progress_percent': progress_percent,
        'user_team': user_team  # ✅ Ajout au contexte
    })


@login_required
def contest_challenge_detail(request, contest_id, challenge_slug):
    user = request.user  # Current user
    contest = get_object_or_404(Contest, id=contest_id)

    # Vérifier si le contest est terminé
    if contest.is_finished():
        return redirect('contest_inscription', contest_id=contest.id)

    # Vérifier si l'utilisateur appartient à une équipe inscrite au contest
    user_team = contest.teams.filter(members=user).first()
    if not user_team:
        return redirect('contest_inscription', contest_id=contest.id)

    # Vérifier si le challenge appartient bien au contest
    challenge = get_object_or_404(Challenge, slug=challenge_slug, contest_challenges__contest=contest)

    # Récupérer les niveaux et fichiers définis
    levels = Level.objects.filter(challenge=challenge).order_by('name')
    defined_files = DefinedFile.objects.filter(level__challenge=challenge).order_by('name')

    # Récupérer les membres de l'équipe
    team_members = user_team.members.all()
    
    # Générer les résultats des tests pour l'utilisateur
    test_results = {}
    for df in defined_files:
        # Vérifie si au moins un membre de l'équipe a validé ce fichier
        is_solved = Performance.objects.filter(definedfile=df, user__in=team_members, solved=True).exists()
        test_results[df.id] = "VALID" if is_solved else "?"
    
    # Mini Leaderboard (Top 5 équipes)
    teams = contest.teams.all()
    leaderboard_data = []

    # Total des fichiers définis du contest
    total_defined_files = DefinedFile.objects.filter(level__challenge__contest_challenges__contest=contest).count() or 1

    for team in teams:
        # Nombre de fichiers résolus par l'équipe
        solved_files = Performance.objects.filter(
            definedfile__level__challenge__contest_challenges__contest=contest,
            user__in=team.members.all(),
            solved=True
        ).values("definedfile").distinct().count()

        # Dernière soumission
        last_performance = Performance.objects.filter(
            user__in=team.members.all(),
            solved=True
        ).aggregate(last=Max("created_at"))["last"] or "2000-01-01"

        # Calcul du score
        score = (solved_files / total_defined_files) * 100

        leaderboard_data.append({
            "team": team,
            "score": round(score, 2),
            "progress": f"{solved_files}/{total_defined_files}",  # Format x/y
            "last_performance": last_performance
        })

    # Trier par score DESC et date ASC
    leaderboard_data.sort(key=lambda x: (-x["score"], x["last_performance"]))

    # Assignation du rang
    for index, entry in enumerate(leaderboard_data):
        entry["rank"] = index + 1

    # Sélectionner uniquement le Top 5
    top_teams = leaderboard_data[:5]

    result = 'Upload your file first'

    if request.method == 'POST':
        uploaded_file = request.FILES.get('uploaded_file')
        if uploaded_file:
            uploaded_content = uploaded_file.read().decode('utf-8').replace('\r\n', '\n').replace('\r', '\n').rstrip('\n')
            defined_file_name = request.POST.get('defined_file_name', None)

            if defined_file_name:
                try:
                    defined_file = DefinedFile.objects.get(name=defined_file_name, level__challenge=challenge)
                    defined_content = defined_file.output_file.read().decode('utf-8').replace('\r\n', '\n').replace('\r', '\n').rstrip('\n')

                    if uploaded_content == defined_content:
                        Performance.objects.create(user=user, definedfile=defined_file, solved=True)
                        result = 'VALID'
                    else:
                        result = 'INVALID'

                except DefinedFile.DoesNotExist:
                    result = f'INVALID (No defined file named {defined_file_name} found for challenge: {challenge.name})'
            else:
                result = 'INVALID (No defined file name provided)'
        else:
            result = 'INVALID (No file uploaded)'

        return JsonResponse({'result': result})

    return render(request, 'contest/contest_challenge_detail.html', {
        'contest': contest,
        'challenge': challenge,
        'levels': levels,
        'defined_files': defined_files,
        'test_results': test_results,
        'user_team': user_team,  # ✅ Ajout du user_team
        'top_teams': top_teams  # ✅ Ajout du leaderboard
    })


def get_contest_score(self, user):
    return self.challenges.filter(levels__defined_files__performance__user=user, levels__defined_files__performance__solved=True).count()

@login_required
def contest_inscription(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    current_time = timezone.now()
    user = request.user

    # ✅ Vérifier si l'utilisateur appartient à une équipe INSCRITE au contest
    user_team = Team.objects.filter(members=user).first()
    team_already_in_contest = contest.teams.filter(members=user).exists()

    # ✅ Récupérer toutes les teams et les demandes en attente
    teams = Team.objects.all()
    pending_requests = Team.objects.filter(join_requests__user=user, join_requests__status='pending')

    # ✅ Initialisation des variables
    button_state = 'disabled'
    button_message = 'Over : See Leaderboard'
    redirect_url = None
    method = 'GET'

    # ✅ Gérer l'affichage du bouton d'inscription
    if contest.is_finished():
        button_state = 'enabled'
        button_message = 'Over : See Leaderboard'
        redirect_url = 'contest_leaderboard'
    elif current_time < contest.start_date:
        # ✅ Contest pas encore commencé
        if team_already_in_contest:
            button_state = 'disabled'
            button_message = 'Enrolled'
        else:
            button_state = 'enabled'
            button_message = 'Participate'
            redirect_url = 'list_teams'
            method = 'POST'
    elif contest.is_active():
        # ✅ Contest en cours
        if team_already_in_contest:
            button_state = 'enabled'
            button_message = 'Join'
            redirect_url = 'contest_detail'
            method = 'POST'
        else:
            button_state = 'enabled'
            button_message = 'Participate'
            redirect_url = 'list_teams'
            method = 'POST'

    return render(request, 'contest/contest_inscription.html', {
        'contest': contest,
        'button_state': button_state,
        'button_message': button_message,
        'redirect_url': redirect_url,
        'method': method,
        'teams': teams,
        'user_team': user_team,
        'pending_requests': pending_requests,
    })



    
@login_required
def contest_participate(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    user = request.user

    if request.method == 'POST':
        if user not in contest.participants.all():
            # ✅ Add the user as a participant
            contest.participants.add(user)

        # ✅ If the contest is active, redirect to contest_detail
        if contest.is_active():
            return redirect('contest_detail', contest_id=contest.id)

    # ✅ If contest is NOT active, stay on the same page (contest_inscription)
    return redirect('contest_inscription', contest_id=contest.id)
