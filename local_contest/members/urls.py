from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import CustomPasswordChangeForm, CustomPasswordResetForm, CustomPasswordResetConfirmForm
from .views import CustomPasswordChangeView, CustomPasswordResetView, CustomPasswordResetConfirmView

urlpatterns = [
    path('login_user', views.login_user, name='login'),
    path('logout_user', views.logout_user, name='logout'),
    path('register_user', views.register_user, name='register'),
    path('profile', views.profile, name='profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('change-password/', CustomPasswordChangeView.as_view(
            form_class=CustomPasswordChangeForm,
            template_name='change_password.html'
        ), name='change_password'),
    
    path('password-reset/', CustomPasswordResetView.as_view(
        form_class=CustomPasswordResetForm,
        template_name='reset_password.html'
        ), name='password_reset'),
        
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(
        form_class=CustomPasswordResetConfirmForm,
        template_name='password_reset_confirm.html'
    ), name='password_reset_confirm'),

]