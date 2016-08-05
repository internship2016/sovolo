# coding=utf-8
from django.utils import timezone
from django.db import models

from tag.models import Tag

# Create your models here.

class User(models.Model):

    # Numbers are arbitrary
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    password = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100)
    birthday = models.DateField()
    telephone = models.CharField(max_length=11)
    emergency_contact = models.CharField(max_length=11)
    email = models.CharField(max_length=200)
    occupation = models.CharField(max_length=100)
    # regionは地方自治体コードで指定
    region = models.IntegerField()
    fb_access_token = models.CharField(max_length=100)
    twitter_access_token = models.CharField(max_length=100)

    follow_tag = models.ManyToManyField(Tag, related_name='follower')

    def save(self, *args, **kwargs):
        # On save, update timestamps
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(User, self).save(*args, **kwargs)
