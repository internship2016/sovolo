# coding=utf-8
from django.db import models
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from user.models import User
from base.models import AbstractBaseModel
from django.conf import settings
from django.contrib import admin
from django.db.models import Q
from django.utils import timezone
from tag.models import Tag
from datetime import datetime

from PIL import Image
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
import os


class Event(AbstractBaseModel):
    # Numbers are arbitrary
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    meeting_place = models.CharField(max_length=400)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    contact = models.CharField(max_length=200)
    details = models.TextField()
    notes = models.TextField(blank=True)
    private_notes = models.TextField(blank=True)
    hashtag = models.CharField(max_length=100, blank=True)
    share_message = models.CharField(max_length=100, blank=True)
    host_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='host_event',
    )
    supporter = models.ManyToManyField(User, related_name="support", blank=True)

    # regionは都道府県で指定
    prefectures = settings.PREFECTURES
    region_list = [(key, value[0]) for key, value in sorted(prefectures.items(), key=lambda x:x[1][1])]
    region = models.CharField(max_length=10, choices=region_list)

    participant = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='participating_event',
        through='Participation',
        blank=True,
    )
    admin = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='admin_event',
        blank=True,
    )

    tag = models.ManyToManyField(Tag, blank=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('event:detail', kwargs={'pk': self.id})

    def save(self, *args, **kwargs):
        return super(Event, self).save(*args, **kwargs)

    def get_image_url(self):
        if self.image:
            return self.image.url
        else:
            return os.path.join(
                settings.MEDIA_URL,
                'events/',
                "default_event_image.jpg",
            )

    def get_tags_as_string(self):
        return "\n".join([tag.name for tag in self.tag.all()])

    def is_full(self):
        frames = Frame.objects.filter(event=self)
        for frame in frames:
            if not frame.is_full():
                return False

        return True

    def is_closed(self):
        frames = Frame.objects.filter(event=self)
        for frame in frames:
            if not frame.is_closed():
                return False

        return True

    def is_over(self):
        return timezone.now() > self.start_time

    def get_status(self):
        if self.is_over():
            return "終了"
        elif self.is_closed():
            return "締め切り済み"
        elif self.is_full():
            return "満員"
        else:
            return "募集中"

    def get_region_kanji(self):
        region = self.prefectures.get(self.region)
        if not region:
            return '未設定'  # XXX: regionがこない場合は未設定でいいのか
        return region[0]

    def start_time_format(self):
        #return self.start_time.strftime("%m/%d %H:%M")
        #return datetime.strptime(self.start_time, "%m/%d %H:%M")
        return self.start_time

    def end_time_format(self):
        #return self.end_time.strftime("%m/%d %H:%M")
        return self.end_time

class EventAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'created', 'modified', 'get_tags_as_string')


class Frame(AbstractBaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    description = models.TextField(default='通常参加枠')
    upper_limit = models.IntegerField(blank=True, null=True)
    deadline = models.DateTimeField()

    def __str__(self):
        return "Frame #" + str(self.pk) + " in Event #" + str(self.event_id)

    def is_full(self):
        if self.upper_limit:
            participant_query = Q(frame=self)
            status_query = Q(status="参加中")
            num_participants = Participation.objects.filter(participant_query & status_query).count()

            return num_participants >= self.upper_limit
        else:
            return True

    def is_closed(self):
        return timezone.now() > self.deadline

    def num_participants(self):
        status_query = Q(status="参加中")
        return self.participation_set.filter(status_query).count()

    def deadline_format(self):
        return self.deadline.strftime("%m/%d %H:%M")

    def participant_id_list(self):
        return self.participation_set.all().values_list('user',flat=True)

    def reserved_id_list(self):
        return self.participation_set.filter(status="参加中").values_list('user',flat=True)

    def waiting_id_list(self):
        return self.participation_set.filter(status="キャンセル待ち").values_list('user',flat=True)


class FrameAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'event',
        'description',
        'upper_limit',
        'deadline',
    )


class Participation(AbstractBaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=30)
    frame = models.ForeignKey(Frame, blank=True, null=True)

    class Meta:
        unique_together = (('event', 'user'),)

    def __str__(self):
        return "Participant:" + self.user.username +", Status: " + self.status

    def save(self, *args, **kwargs):
        return super(Participation, self).save(*args, **kwargs)


class ParticipationAdmin(admin.ModelAdmin):
    list_display = ['pk', 'event', 'user', 'status', 'frame']


class Comment(AbstractBaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        null=True
    )

    def __str__(self):
        if self.reply_to:
            return ">> %s\n%s :\"%s" % (
                str(self.reply_to),
                self.user.username,
                self.text,
            )
        else:
            return "%s: \"%s\"" % (
                self.user.username,
                self.text,
            )

    def get_absolute_url(self):
        return reverse('event:detail', kwargs={'pk': self.event.id})

    def save(self, *args, **kwargs):
        return super(Comment, self).save(*args, **kwargs)


class Question(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='question',
    )
    question = models.TextField()

    def __str__(self):
        return self.question


class Answer(AbstractBaseModel):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answer',
    )
    participation = models.ForeignKey(
        Participation,
        on_delete=models.CASCADE,
        related_name='answer',
    )
    text = models.TextField()

    def __str__(self):
        return "Q: " + self.question.question + " -> " + "A: " + self.text

    def save(self, *args, **kwargs):
        return super(Answer, self).save(*args, **kwargs)
