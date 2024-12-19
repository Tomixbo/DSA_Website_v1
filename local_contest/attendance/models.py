from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AttendanceCode(models.Model):
    code = models.CharField(max_length=10, unique=True)
    generated_at = models.DateTimeField(auto_now=True)

class UserAttendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    code_used = models.CharField(max_length=10)
    presence_validated = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'date')  # Un utilisateur ne peut valider sa présence qu'une fois par jour.
