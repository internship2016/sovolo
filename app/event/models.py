# coding=utf-8
from django.utils import timezone

from django.db import models
from user.models import User

# Create your models here.

class Event(models.Model):
    #Numbers are arbitrary
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    meeting_place = models.CharField(max_length=400)
    place = models.CharField(max_length=400)
    longitude = models.FloatField()
    latitude = models.FloatField()
    image = models.ImageField(upload_to='events/')
    contact = models.CharField(max_length=200)
    details = models.TextField()
    notes = models.TextField()
    ticket = models.BooleanField()
    hashtag = models.CharField(max_length=100)
    share_message = models.CharField(max_length=100)
    host_user = models.ForeignKey(User, related_name='host_event')
    #regionは地方自治体コードで指定
    region = models.IntegerField()

    participant = models.ManyToManyField(User, through='Participation')
    admin = models.ManyToManyField(User, related_name='admin_event')

    def save(self, *args, **kwargs):
        # On save, update timestamps
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Event, self).save(*args, **kwargs)

class Frame(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    description = models.TextField()
    lower_limit = models.IntegerField()
    upper_limit = models.IntegerField()
    deadline = models.DateTimeField()
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField()

    def save(self, *args, **kwargs):
        # On save, update timestamps
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Frame, self).save(*args, **kwargs)


class Participation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10)
    created = models.DateTimeField(editable=False)
    frame = models.ForeignKey(Frame)
    modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        # On save, update timestamps
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Participation, self).save(*args, **kwargs)

class Comment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField()

    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies')

    def save(self, *args, **kwargs):
        # On save, update timestamps
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Comment, self).save(*args, **kwargs)

class Question(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    question = models.TextField()

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField()

    def save(self, *args, **kwargs):
        # On save, update timestamps
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Answer, self).save(*args, **kwargs)