from django.db.models.signals import post_save
from django.dispatch import receiver

from realworld.apps.profiles.models import Profile

from .models import JwtUser


@receiver(post_save, sender=JwtUser)
def create_related_profile(sender, instance, created, *args, **kwargs):
    if instance and created:
        instance.profile = Profile.objects.create(user=instance)
