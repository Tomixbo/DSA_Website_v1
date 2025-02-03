from django.db import models
from django.utils import timezone
from challenges.models import Challenge
from teams.models import Team
from django.utils.text import slugify

class Contest(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    teams = models.ManyToManyField(Team, related_name='contests', blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date
    
    def is_finished(self):
        now = timezone.now()
        return now > self.end_date


class ContestChallenge(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="contest_challenges")
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name="contest_challenges")

    class Meta:
        unique_together = ('contest', 'challenge')  # ✅ Empêche d'ajouter un même challenge deux fois dans un contest

    def __str__(self):
        return f"{self.challenge.name} in {self.contest.name}"
