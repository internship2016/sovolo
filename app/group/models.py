# coding=utf-8
from django.utils import timezone
from django.db import models
from user.models import User
from event.models import Event
from django.conf import settings
from django.core.urlresolvers import reverse

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

    member = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Membership',
        blank=True,
    )

    description = models.TextField()

    def admins(self):
        return self.member.filter(membership__role='admin')

    def members(self):
        return self.member.filter(membership__role='Normal')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        return super(Group, self).save(*args, **kwargs)

    def get_image_url(self):
        if self.image:
            return self.image.url
        else:
            return os.path.join(
                settings.MEDIA_URL,
                'group/',
                "default_group_image.jpg",
            )

    def get_absolute_url(self):
        return reverse('group:detail', kwargs={'pk': self.id})


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'modified')


class Membership(models.Model):
    member = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    role = models.CharField(max_length=20, default='Normal')

    class Meta:
        unique_together = (('group', 'member'),)
