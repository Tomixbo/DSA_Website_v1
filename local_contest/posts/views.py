from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from .models import Post
from .forms import PostForm
from django.http import JsonResponse

def is_staff(user):
    return user.is_staff

@permission_required('is_staff')
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})

@login_required
def post_list(request):
    posts = Post.objects.all().order_by('-date', '-time')  # Trie par date et heure décroissantes
    return render(request, 'post_list.html', {'posts': posts})

def create_post_ajax(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        if content:
            post = Post.objects.create(description=content, image=image, author=request.user)
            return JsonResponse({'message': 'Post créé avec succès'})
        else:
            return JsonResponse({'message': 'Contenu du post requis'})
    else:
        return JsonResponse({'message': 'Méthode non autorisée'})
    
# fonction pour liker
def like_post(request, post_id):
    print("La vue like_post a été appelée")
    if request.method == 'POST':
        post = Post.objects.get(id=post_id)
        post.like()
        return JsonResponse({'likes': post.likes})
    else:
        return JsonResponse({'error': 'Méthode non autorisée'})