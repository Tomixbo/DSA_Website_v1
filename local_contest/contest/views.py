from django.shortcuts import render, get_object_or_404, redirect
from .models import Competition
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from members.models import CustomUser
from django.utils.timesince import timesince
from datetime import timedelta

def competition_list(request):
    competitions = Competition.objects.all().order_by('name')

    # Filter by name
    name_query = request.GET.get('name', '')
    if name_query:
        competitions = competitions.filter(name__icontains=name_query)

    # Filter by start_time
    start_time_query = request.GET.get('start_time', '')
    if start_time_query:
        competitions = competitions.filter(start_time__gte=start_time_query)

    # Filter by end_time
    end_time_query = request.GET.get('end_time', '')
    if end_time_query:
        competitions = competitions.filter(end_time__lte=end_time_query)

    no_competitions_message = "There are no competitions yet." if not competitions.exists() else None

    return render(request, 'contest/competition_list.html', {
        'competitions': competitions,
        'name_query': name_query,
        'start_time_query': start_time_query,
        'end_time_query': end_time_query,
        'no_competitions_message': no_competitions_message
    })

@login_required
def competition_detail(request, pk):
    competition = get_object_or_404(Competition, pk=pk)
    current_time = timezone.now()
    user = request.user

    # Check if the user is already a participant
    is_participant = user in competition.participants.all()

    # Initialize variables
    button_state = 'disabled'
    button_message = 'The competition is over.'
    redirect_url = None

    if competition.is_finished():
        # Competition is over
        button_state = 'disabled'
        button_message = 'The competition is over.'
    elif current_time < competition.start_time:
        # Competition has not started yet
        if is_participant:
            button_state = 'enabled'
            button_message = 'Join'
            redirect_url = 'competition_time_left'
        else:
            button_state = 'enabled'
            button_message = 'Participate'
            redirect_url = 'competition_participate'
    elif competition.is_active():
        # Competition is ongoing
        if is_participant:
            button_state = 'enabled'
            button_message = 'Enrolled'
            redirect_url = 'competition_challenges'

    return render(request, 'contest/competition_detail.html', {
        'competition': competition,
        'button_state': button_state,
        'button_message': button_message,
        'is_participant': is_participant,
        'redirect_url': redirect_url,
        'current_time': current_time
    })

@login_required
def competition_participate(request, pk):
    competition = get_object_or_404(Competition, pk=pk)
    user = request.user

    if request.method == 'POST':
        if user in competition.participants.all():
            return redirect('competition_detail', pk=competition.pk)
        competition.participants.add(user)
        return redirect('competition_detail', pk=competition.pk)

    return render(request, 'contest/competition_participate.html', {
        'competition': competition
    })

@login_required
def competition_time_left(request, pk):
    competition = get_object_or_404(Competition, pk=pk)
    current_time = timezone.now()
    time_left = competition.start_time - current_time

    return render(request, 'contest/competition_time_left.html', {
        'competition': competition,
        'time_left_days': time_left.days,
        'time_left_hours': time_left.seconds // 3600,
        'time_left_minutes': (time_left.seconds // 60) % 60
    })

@login_required
def competition_challenges(request, pk):
    competition = get_object_or_404(Competition, pk=pk)
    user = request.user

    # Check if the user is a participant
    is_participant = user in competition.participants.all()

    if not is_participant:
        return redirect('competition_participate', pk=competition.pk)

    # Logic for displaying challenges
    # Example: challenges = Challenge.objects.filter(competition=competition)

    return render(request, 'contest/competition_challenges.html', {
        'competition': competition,
        # 'challenges': challenges
    })