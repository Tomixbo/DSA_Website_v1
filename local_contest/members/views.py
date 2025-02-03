from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterUserForm
from challenges.utils import update_ranks, calculate_rank, calculate_score, update_ranks, update_score, update_category
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import CustomUser
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy


def login_user(request):
    if request.user.is_authenticated:
        update_ranks()
        return redirect('challenge_list')
    else:
        if request.method == "POST":
            username = request.POST["username"].lower()
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, (f"You were logged as : {username.capitalize()}"))
                return redirect('post_list')
                
            else:
                messages.success(request, ("Error : verify username/password, and try again..."))
                return redirect('login')
        else:
            return render(request, 'authenticate/login.html', {})

def logout_user(request):
    messages.success(request, ("You were logged out!"))
    logout(request)
    return redirect('login')

def register_user(request):
    if request.user.is_authenticated:
        return redirect('challenge_list')
    else:
        if request.method == "POST":
            form = RegisterUserForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data['username'].lower()
                password = form.cleaned_data['password1']
                user = authenticate(username=username, password=password)
                login(request, user)
                messages.success(request, ("Registration successfull! Welcome to DSA-INSI"))
                return redirect('challenge_list')
            else:
                messages.error(request, (form.errors))

        else:
            form = RegisterUserForm()

        return render(request, 'authenticate/register_user.html', {'form':form,})

@login_required
def profile(request):
    user = request.user
    rank, total_user = calculate_rank(user)
    graduation_choices = CustomUser.GRADUATION_CHOICES
    return render(request, 'profile.html', {'user':user, 'total_user': total_user, 'graduation_choices': graduation_choices})

@login_required
def update_profile(request):
    if request.method == 'POST':
        field = request.POST.get('field')
        value = request.POST.get('value')
        user = request.user

        if field == 'first_name':
            user.first_name = value
        elif field == 'last_name':
            user.last_name = value
        elif field == 'username':
            user.username = value.lower()
        elif field == 'email':
            user.email = value
        elif field == 'graduation_field':
            user.graduation_field = value

        user.save()
        return JsonResponse({'status': 'success', 'value': value})

    return JsonResponse({'status': 'error'}, status=400)

class CustomPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('challenge_list')
    def form_valid(self, form):
        # Add success message
        messages.success(self.request, "Your password has been changed successfully!")

        # Redirect to the 'challenge_list' URL
        return super().form_valid(form)

class CustomPasswordResetView(PasswordResetView):
    success_url = reverse_lazy('login')
    def form_valid(self, form):
        # Add success message
        messages.success(self.request, "We've sent you an email to reset your password!")

        # Redirect to the 'challenge_list' URL
        return super().form_valid(form)

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        # Add success message
        messages.success(self.request, "Your password has been reseted")

        # Redirect to the 'challenge_list' URL
        return super().form_valid(form)