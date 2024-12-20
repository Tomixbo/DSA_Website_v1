from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import capfirst

class CustomUser(AbstractUser):
    GRADUATION_CHOICES = [
        ('L1_v1', 'L1_v1'),
        ('L1_v2', 'L1_v2'),
        ('L2_IAD', 'L2_IAD'),
        ('L2_GL', 'L2_GL'),
        ('L2_ARSB', 'L2_ARSB'),
        ('L3_IAD', 'L3_IAD'),
        ('L3_GL', 'L3_GL'),
        ('L3_ARSB', 'L3_ARSB'),
    ]
    CATEGORY_CHOICES = [
        ('Alpha', 'Alpha'),
        ('Beta', 'Beta'),
        ('Gamma', 'Gamma'),
        ('Omega', 'Omega'),
    ]
    graduation_field = models.CharField(max_length=10, choices=GRADUATION_CHOICES, default='L1_v1')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='Alpha')

    rank = models.IntegerField(default=0)
    score = models.IntegerField(default=0)


@receiver(pre_save, sender=CustomUser)
def capitalize_names(sender, instance, **kwargs):
    # Convertir last_name en majuscules
    instance.last_name = instance.last_name.upper()

    # Convertir first_name en majuscule en début de phrase
    instance.first_name = capfirst(instance.first_name)