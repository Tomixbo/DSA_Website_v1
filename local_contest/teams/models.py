from django.conf import settings
from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="teams", blank=True)  
    
    def __str__(self):
        return self.name

class TeamRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  

class JoinRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='join_requests')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='join_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    def accept(self):
        """Accepter la demande, ajouter l'utilisateur à l'équipe, puis supprimer la demande."""
        self.team.members.add(self.user)
        self.delete()  # ✅ Delete request after acceptance

    def reject(self):
        """Rejeter la demande et la supprimer."""
        self.delete()  # ✅ Delete request after rejection

    def __str__(self):
        return f"Request from {self.user.username} to join {self.team.name}"


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    join_request = models.ForeignKey(JoinRequest, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
class Invitation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Rejetée'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invitations")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="invitations")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def accept(self):
        """Accepter l'invitation, ajouter l'utilisateur à l'équipe, puis supprimer l'invitation."""
        self.team.members.add(self.user)
        self.delete()  # ✅ Delete invitation after acceptance

    def reject(self):
        """Rejeter l'invitation et la supprimer."""
        self.delete()  # ✅ Delete invitation after rejection

    def __str__(self):
        return f"Invitation for {self.user.username} to join {self.team.name}"
