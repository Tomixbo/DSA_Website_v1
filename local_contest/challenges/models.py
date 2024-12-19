from django.db import models
from django.utils.text import slugify
import os
from members.models import CustomUser
from django.utils import timezone

class Challenge(models.Model):
    CATEGORY_CHOICES = [
        ('Alpha', 'Alpha'),
        ('Beta', 'Beta'),
        ('Gamma', 'Gamma'),
        ('Omega', 'Omega'),
    ]
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(null=True, blank=True)
    author = models.CharField(max_length=100, blank = True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='Alpha')
    difficulty = models.IntegerField(default=1, choices=[(i, i) for i in range(1, 6)])  # Level field with choices 1 to 5
    published = models.BooleanField(default=False)
    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Level(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    # Add any other fields for levels as needed
    def upload_to_description_file(instance, filename):
        challenge_slug = instance.challenge.slug
        return f'{challenge_slug}/level_descriptions/{filename}'

    def upload_to_input_file(instance, filename):
        challenge_slug = instance.challenge.slug
        return f'{challenge_slug}/level_input_files/{filename}'
    
    
    description_file = models.FileField(upload_to=upload_to_description_file, null=True, blank=True)
    input_file = models.FileField(upload_to=upload_to_input_file, null=True, blank=True)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='levels')

    

    def __str__(self):
        return self.name


class DefinedFile(models.Model):
    name = models.CharField(max_length=100)

    def upload_to_input_file(instance, filename):
        if instance.level:
            return f"{instance.level.challenge.slug}/level_input_files/{instance.level.name}/{filename}"
        else:
            return "level_input_files/" + filename
    
    def upload_to_output_file(instance, filename):
        if instance.level:
            return f"{instance.level.challenge.slug}/level_output_files/{instance.level.name}/{filename}"
        else:
            return "level_output_files/" + filename

    input_file = models.FileField(upload_to=upload_to_input_file, null=True, blank=True)
    output_file = models.FileField(upload_to=upload_to_output_file, null=True, blank=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='defined_files') 
    
    def __str__(self):
        return self.name
    
    def filename(self):
        return os.path.basename(self.input_file.name)
    
    def get_test_result(self, user):
        try:
            performance = Performance.objects.get(user=user, definedfile=self)
            return "VALID" if performance.solved else "?"
        except Performance.DoesNotExist:
            return "?"
    
    def get_test_result_for_user(self, request):
        return self.get_test_result(request.user)

    
class Performance(models.Model):
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    definedfile = models.ForeignKey(DefinedFile, on_delete=models.CASCADE)
    solved = models.BooleanField(default=False)
    description = models.CharField(max_length=150)
    created_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        # Si la performance n'a pas de description, créez-la à partir du nom d'utilisateur et de la date de création
        if not self.created_at:  # If the object is being created for the first time
            self.created_at = timezone.now()  # Set the creation timestamp
        if not self.description:
            self.description = f"{self.user.username}_{self.created_at.strftime('%Y-%m-%d_%H-%M-%S')}"
        
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ['user', 'definedfile']