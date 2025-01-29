from django.db import models
from challenges.models import Challenge
from django.utils import timezone  # ✅ Bon import

class Contest(models.Model):
    name = models.CharField(max_length=100, unique=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    challenges = models.ManyToManyField(Challenge, related_name="contests")

    def __str__(self):
        return self.name

    def is_active(self):
        """ Vérifie si le contest est en cours """
        now = timezone.now()
        return self.start_date <= now <= self.end_date
    
    def is_finished(self):
        now = timezone.now()
        return now > self.end_date
