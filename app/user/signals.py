from django.utils import translation
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User


@receiver(post_save, sender=User, dispatch_uid="set_language_count")
def set_language(sender, instance, **kwargs):
    translation.activate(instance.language)
    # request.session[translation.LANGUAGE_SESSION_KEY] = instance.language
