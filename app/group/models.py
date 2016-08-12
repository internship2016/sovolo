# coding=utf-8
from django.utils import timezone
from django.db import models
from user.models import User
from event.models import Event
from django.conf import settings

from PIL import Image
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

from base.models import AbstractBaseModel
from django.contrib import admin
import os

# Create your models here.


class Group(AbstractBaseModel):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='group/', blank=True, null=True)

    event = models.ManyToManyField(Event, blank=True)

    member = models.ManyToManyField(settings.AUTH_USER_MODEL)

    description = models.TextField()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        return super(Group, self).save(*args, **kwargs)

    def get_image_url(self):
        if self.image is not None:
            return self.image
        else:
            return os.path.join(
                settings.MEDIA_URL,
                'groups/',
                "default_group_image.jpg",
            )

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'modified')

class Membership(models.Model):
    member = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    role = models.CharField(max_length=20, default='Normal')
