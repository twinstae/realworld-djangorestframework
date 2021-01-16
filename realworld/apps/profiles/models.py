from django.contrib.auth.models import User
from django.db import models

from realworld.apps.core.models import TimestampedModel


class Profile(TimestampedModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE
    )
    bio = models.TextField(blank=True)
    image = models.URLField(blank=True)
    follows = models.ManyToManyField(
        'self',
        related_name='followed_by',
        symmetrical=False
    )

    def __str__(self):
        return self.user.username

    def follow(self, profile):
        self.follows.add(profile)

    def unfollow(self, profile):
        self.follows.remove(profile)

    def is_following(self, profile):
        return self.follows.filter(pk=profile.pk).exists()

    def is_followed_by(self, profile):
        return self.is_followed_by.filter(pk=profile.pk).exists()
