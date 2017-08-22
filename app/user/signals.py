from django.utils import translation
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import User


@receiver(post_save, sender=User, dispatch_uid="set_language_count")
def edit_set_language(sender, instance, **kwargs):
    translation.activate(instance.language)


@receiver(user_logged_in, sender=User, dispatch_uid="set_language_count")
def login_set_language(request, user, **kwargs):
    translation.activate(user.language)
    request.session[translation.LANGUAGE_SESSION_KEY] = user.language
