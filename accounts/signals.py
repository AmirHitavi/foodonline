from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, UserProfile


@receiver(post_save, sender=User)
def post_save_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create a profile when user is created.
        UserProfile.objects.create(user=instance)
    else:
        try:
            # update the profile for the user already created
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except UserProfile.DoesNotExist:
            # create a profile for user that already created but don't have a profile
            UserProfile.objects.create(user=instance)
