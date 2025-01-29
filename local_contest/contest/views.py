from django.shortcuts import render, get_object_or_404, redirect
from .models import Contest
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from challenges.models import Challenge, Level, DefinedFile, Performance
from django.db.models import Count, Q, OuterRef, Subquery
from django.utils import timezone


@login_required
def contest_list(request):
    contests = Contest.objects.all().order_by('-start_date')
    return render(request, 'contest/contest_list.html', {'contests': contests})



@login_required
def contest_detail(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    user = request.user  # Get current user

    # ✅ Redirect if the contest is finished
    if contest.is_finished():
        return redirect('contest_inscription', contest_id=contest.id)

    # ✅ Redirect if the user is NOT a participant
    if user not in contest.participants.all():
        return redirect('contest_inscription', contest_id=contest.id)

    # ✅ Get all challenges associated with the contest
    challenges = Challenge.objects.filter(contest_challenges__contest=contest).order_by('category', 'name')

    # ✅ Subqueries for counting total defined files per challenge
    defined_files_count = Challenge.objects.filter(
        pk=OuterRef('pk')
    ).annotate(
        count=Count('levels__defined_files')
    ).values('count')

    # ✅ Subqueries for counting solved defined files per challenge (for this user)
    resolved_files_count = Challenge.objects.filter(
        pk=OuterRef('pk')
    ).annotate(
        count=Count('levels__defined_files', filter=Q(levels__defined_files__performance__user=user, levels__defined_files__performance__solved=True))
    ).values('count')

    # ✅ Annotate challenges with progress data
    challenges = challenges.annotate(
        num_defined_files=Subquery(defined_files_count),
        num_resolved_defined_files=Subquery(resolved_files_count)
    )

    # ✅ Compute total defined and resolved files using the queryset annotations
    total_defined_files = sum(ch.num_defined_files or 0 for ch in challenges)
    total_resolved_files = sum(ch.num_resolved_defined_files or 0 for ch in challenges)

    # ✅ Calculate contest-wide progress percentage
    progress_percent = (total_resolved_files / total_defined_files) * 100 if total_defined_files > 0 else 0

    return render(request, 'contest/contest_detail.html', {
        'contest': contest,
        'challenges': challenges,
        'progress_percent': progress_percent
    })


@login_required
def contest_challenge_detail(request, contest_id, challenge_slug):
    user = request.user  # Current user

    contest = get_object_or_404(Contest, id=contest_id)

    # ✅ Redirect if the contest is finished
    if contest.is_finished():
        return redirect('contest_inscription', contest_id=contest.id)

    # ✅ Ensure user is a participant
    if user not in contest.participants.all():
        return redirect('contest_inscription', contest_id=contest.id)

    # ✅ Ensure challenge belongs to contest
    challenge = get_object_or_404(Challenge, slug=challenge_slug, contest_challenges__contest=contest)

    # ✅ Get levels and defined files
    levels = Level.objects.filter(challenge=challenge).order_by('name')
    defined_files = DefinedFile.objects.filter(level__challenge=challenge).order_by('name')

    # ✅ Generate test results for the user
    test_results = {df.id: df.get_test_result_for_user(request) for df in defined_files}

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
        'test_results': test_results
    })

def get_contest_score(self, user):
    return self.challenges.filter(levels__defined_files__performance__user=user, levels__defined_files__performance__solved=True).count()

@login_required
def contest_inscription(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    current_time = timezone.now()
    user = request.user

    # Check if the user is already a participant
    is_participant = user in contest.participants.all()

    # Initialize variables
    button_state = 'disabled'
    button_message = 'Over : See Leaderboard'
    redirect_url = None
    method = 'GET'

    if contest.is_finished():
        # Contest is over
        button_state = 'disabled'
        button_message = 'Over : See Leaderboard'
    elif current_time < contest.start_date:
        # Contest has not started yet
        if is_participant:
            button_state = 'disabled'
            button_message = 'Enrolled'
        else:
            button_state = 'enabled'
            button_message = 'Participate'
            redirect_url = 'contest_participate'
            method = 'POST'
    elif contest.is_active():
        # Contest is ongoing
        if is_participant:
            button_state = 'enabled'
            button_message = 'Join'
            redirect_url = 'contest_detail'
            method = 'POST'
        else:
            button_state = 'enabled'
            button_message = 'Participate'
            redirect_url = 'contest_participate'
            method = 'POST'

    return render(request, 'contest/contest_inscription.html', {
        'contest': contest,
        'button_state': button_state,
        'button_message': button_message,
        'is_participant': is_participant,
        'redirect_url': redirect_url,
        'current_time': current_time,
        'method': method
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
