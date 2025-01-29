from django.shortcuts import render, get_object_or_404
from .models import Contest
from challenges.models import Challenge

def contest_list(request):
    contests = Contest.objects.all().order_by('-start_date')
    return render(request, 'contest/contest_list.html', {'contests': contests})

def contest_detail(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    challenges = contest.challenges.all()
    return render(request, 'contest/contest_detail.html', {'contest': contest, 'challenges': challenges})

def contest_challenge_detail(request, contest_id, challenge_slug):
    contest = get_object_or_404(Contest, id=contest_id)
    challenge = get_object_or_404(Challenge, slug=challenge_slug, contests=contest)

    return render(request, 'challenge_detail.html', {'challenge': challenge, 'contest': contest})

def get_contest_score(self, user):
    return self.challenges.filter(levels__defined_files__performance__user=user, levels__defined_files__performance__solved=True).count()

