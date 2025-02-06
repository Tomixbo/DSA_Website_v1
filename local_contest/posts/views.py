from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from .models import Post, PinnedPost
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

    pinned_post = PinnedPost.get_pinned()
    if pinned_post:  # Ensure pinned_post exists before accessing attributes
        pinned_post.description = mark_safe(markdown.markdown(pinned_post.description))


    # Retrieve posts, excluding the pinned one
    posts = Post.objects.exclude(id=pinned_post.id if pinned_post else None).order_by('-date', '-time')
    for post in posts:
        post.description = mark_safe(markdown.markdown(post.description))

    # Get the TOP 10 ranking users
    ranking_users = CustomUser.objects.order_by('rank')[:10]

    # 1) Fetch the 2 most recent contests
    contests = Contest.objects.all().order_by('-start_date')[:2]

    # 2) Fetch 5 random published challenges
    excluded_challenges = ContestChallenge.objects.values_list('challenge_id', flat=True)
    random_challenges = Challenge.objects.exclude(id__in=excluded_challenges).filter(published=True).order_by('?')[:3]

    return render(request, 'post_list.html', {
        'form': form,
        'pinned_post': pinned_post,  # Pass pinned post to the template
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

@login_required
def pin_post(request, post_id):
    if request.user.is_staff:
        post = get_object_or_404(Post, id=post_id)
        PinnedPost.set_pinned(post)  # Set the pinned post
    return redirect('post_list')

@login_required
def unpin_post(request):
    if request.user.is_staff:
        pinned_post = PinnedPost.objects.first()
        if pinned_post:
            pinned_post.post = None
            pinned_post.save()
    return redirect('post_list')
