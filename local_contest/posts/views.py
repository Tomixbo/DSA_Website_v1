from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from .models import Post
from .forms import PostForm
from django.http import JsonResponse
import markdown
from django.utils.safestring import mark_safe
from members.models import CustomUser
from contest.models import Contest, ContestChallenge
from challenges.models import Challenge


def is_staff(user):
    return user.is_staff


@login_required
def post_list(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_list')
    else:
        form = PostForm()

    # Retrieve your posts
    posts = Post.objects.all().order_by('-date', '-time')
    for post in posts:
        post.description = mark_safe(markdown.markdown(post.description))

    # Get the TOP 10 ranking users
    ranking_users = CustomUser.objects.order_by('rank')[:10]

    # 1) Fetch the 3 most recent contests
    contests = Contest.objects.all().order_by('-start_date')[:3]

    # 2) Fetch 5 random published challenges
    #    (If you want more advanced logic like excluding contest challenges, adapt as needed)
    excluded_challenges = ContestChallenge.objects.values_list('challenge_id', flat=True)
    random_challenges = Challenge.objects.exclude(id__in=excluded_challenges).filter(published=True).order_by('?')[:5]

    return render(request, 'post_list.html', {
        'form': form,
        'posts': posts,
        'ranking_users': ranking_users,
        'contests': contests,
        'random_challenges': random_challenges,
    })

@permission_required('is_staff')
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        post.delete()
    return redirect('post_list')

