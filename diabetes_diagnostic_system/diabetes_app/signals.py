# diabetes_app/signals.py
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def handle_user_profile(sender, instance, created, **kwargs):
    """
    Single signal handler that safely manages user profiles
    Using get_or_create prevents duplicate errors
    """
    Profile.objects.get_or_create(user=instance)
    if hasattr(instance, 'profile'):
        instance.profile.save()