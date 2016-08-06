# coding=utf-8
from django.utils import timezone
from django.db import models
from user.models import User
from event.models import Event
# Create your models here.

class Group(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    image = models.ImageField(upload_to='group/', blank=True)

    event = models.ManyToManyField(Event, blank=True)

    member = models.ManyToManyField(User)

    def save(self, *args, **kwargs):
        # On save, update timestamps
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Group, self).save(*args, **kwargs)

class Membership(models.Model):
    member = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    role = models.CharField(max_length=20, default='Normal')