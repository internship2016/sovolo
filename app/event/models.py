# coding=utf-8
from django.utils import timezone

from django.db import models
from django.core.urlresolvers import reverse
from user.models import User
from base.models import AbstractBaseModel
from django.conf import settings
from django.contrib import admin
from tag.models import Tag

from PIL import Image
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys, os


class Event(AbstractBaseModel):
    #Numbers are arbitrary
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    meeting_place = models.CharField(max_length=400)
    place = models.CharField(max_length=400)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    contact = models.CharField(max_length=200)
    details = models.TextField()
    notes = models.TextField(blank=True)
    ticket = models.BooleanField()
    hashtag = models.CharField(max_length=100, blank=True)
    share_message = models.CharField(max_length=100, blank=True)
    host_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='host_event')
    #regionは地方自治体コードで指定
    region = models.IntegerField()

    participant = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Participation', blank=True)
    admin = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='admin_event', blank=True)

    tag = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('event:detail', kwargs={'pk': self.id})

    def save(self, *args, **kwargs):
        return super(Event, self).save(*args, **kwargs)

    def getImageUrl(self):
        if self.image:
            return self.image.url
        else:
            return os.path.join(settings.MEDIA_URL, 'events/', "default_event_image.jpeg")

class EventAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'created', 'modified')


class Frame(AbstractBaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    description = models.TextField(default='通常参加枠')
    lower_limit = models.IntegerField(blank=True)
    upper_limit = models.IntegerField(blank=True)
    deadline = models.DateTimeField()

    def save(self, *args, **kwargs):
        return super(Frame, self).save(*args, **kwargs)

    def __str__(self):
        return "Frame #%d" %(self.pk)

class FrameAdmin(admin.ModelAdmin):
    list_display = ('pk', 'event', 'description', 'lower_limit', 'upper_limit', 'deadline')

class Participation(AbstractBaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=30)
    frame = models.ForeignKey(Frame, blank=True, null=True)

    class Meta:
        unique_together = (('event', 'user'),)

    def save(self, *args, **kwargs):
        return super(Participation, self).save(*args, **kwargs)


class ParticipationAdmin(admin.ModelAdmin):
    list_display = ['pk', 'event', 'user', 'status', 'frame']


class Comment(AbstractBaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies',null=True)

    def __str__(self):
        if self.reply_to:
            return ">> " + str(self.reply_to) + "\n" + self.user.nickname + " :\"" + self.text
        else:
            return self.user.nickname + ": \"" + self.text

    def save(self, *args, **kwargs):
        return super(Comment, self).save(*args, **kwargs)


class Question(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='question')
    question = models.TextField()

    def __str__(self):
        return self.question


class Answer(AbstractBaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer')
    participation = models.ForeignKey(Participation, on_delete=models.CASCADE, related_name='answer')
    text = models.TextField()

    def __str__(self):
        return "Q: " + self.question.question + " -> " + "A: " + self.text

    def save(self, *args, **kwargs):
        return super(Answer, self).save(*args, **kwargs)