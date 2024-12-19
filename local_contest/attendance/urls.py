from django.urls import path
from attendance import views

app_name = 'attendance'

urlpatterns = [
    path('display_code/', views.display_code, name='display_code'),
    path('validate/', views.validate_attendance, name='validate_attendance'),
]
