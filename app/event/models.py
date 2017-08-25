# coding=utf-8
from django.db import models
from django.core.urlresolvers import reverse
from user.models import User
from base.models import AbstractBaseModel
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from tag.models import Tag
from django.utils.translation import ugettext_lazy as _

import os
import math


class Event(AbstractBaseModel):
    # Numbers are arbitrary
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    meeting_place = models.CharField(max_length=400)
    longitude = models.FloatField(default=139.7191)
    latitude = models.FloatField(default=35.7291)
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    contact = models.CharField(max_length=200)
    details = models.TextField()
    notes = models.TextField(blank=True)
    private_notes = models.TextField(blank=True)
    hashtag = models.CharField(max_length=100, blank=True)
    share_message = models.CharField(max_length=100, blank=True)

    host_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  related_name='host_event')

    supporter = models.ManyToManyField(User,
                                       related_name="support",
                                       blank=True)

    # regionは都道府県で指定
    prefectures = settings.PREFECTURES
    prefs = prefectures.items()
    prefs = sorted(prefs, key=lambda x: x[1][1])
    region_list = [(k, v[0]) for k, v in prefs]
    region = models.CharField(max_length=10, choices=region_list)

    participant = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                         related_name='participating_event',
                                         through='Participation',
                                         blank=True)

    admin = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                   related_name='admin_event',
                                   blank=True)

    tag = models.ManyToManyField(Tag, blank=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return "%(name)s: %(since)s ~ %(until)s" % {
            'name': self.name,
            'since': self.start_time.strftime("%Y-%m-%d"),
            'until': self.end_time.strftime("%Y-%m-%d"),
        }

    def get_absolute_url(self):
        return reverse('event:detail', kwargs={'pk': self.id})

    def save(self, *args, **kwargs):
        return super(Event, self).save(*args, **kwargs)

    def get_image_url(self):
        if self.image:
            return self.image.url
        else:
            return os.path.join(settings.MEDIA_URL,
                                'events/',
                                "default_event_image.svg")

    def get_tags_as_string(self):
        return "\n".join([tag.name for tag in self.tag.all()])

    def is_full(self):
        frames = Frame.objects.filter(event=self)
        return all(frame.is_full() for frame in frames)

    def is_closed(self):
        frames = Frame.objects.filter(event=self)
        return all(frame.is_closed() for frame in frames)

    def is_started(self):
        return timezone.now() > self.start_time

    def is_over(self):
        return timezone.now() > self.end_time

    def get_status(self):
        conv = {'finished': {'label': 'default', 'msg': _("Finished")},
                'in_session': {'label': 'success', 'msg': _("In Session")},
                'closed': {'label': 'default', 'msg': _("Closed")},
                'full': {'label': 'default', 'msg': _("Full")},
                'wanted': {'label': 'info', 'msg': _("Wanted")}}

        if self.is_over():
            return conv['finished']
        elif self.is_started():
            return conv['in_session']
        elif self.is_closed():
            return conv['closed']
        elif self.is_full():
            return conv['full']
        else:
            return conv['wanted']

    def get_region_kanji(self):
        region = self.prefectures.get(self.region)
        if not region:
            return _('Not provided')  # XXX: regionがこない場合は未設定でいいのか
        return region[0]

    def start_time_format(self):
        return self.start_time

    def end_time_format(self):
        return self.end_time

    def get_reserved_users(self):
        participations = self.participation_set \
                             .filter(status="参加中")
        return [p.user for p in participations]

    def get_waiting_users(self):
        participations = self.participation_set \
                             .filter(status="キャンセル待ち") \
                             .order_by('created')
        return [p.user for p in participations]

    def get_host_user_as_list(self):
        return [self.host_user]

    @classmethod
    def get_events_in_range(cls, ne_lat, sw_lat, ne_lng, sw_lng):
        return cls.objects.filter(latitude__gte=sw_lat,
                                  latitude__lte=ne_lat,
                                  longitude__gte=sw_lng,
                                  longitude__lte=ne_lng)


class Frame(AbstractBaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    description = models.TextField(default='通常参加枠')
    upper_limit = models.IntegerField(blank=True, null=True)
    deadline = models.DateTimeField()

    participant = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                         related_name='participating_frame',
                                         through='Participation',
                                         blank=True)

    def __str__(self):
        return "Frame #" + str(self.pk) + " in Event #" + str(self.event_id)

    def is_full(self):
        if self.upper_limit is None:
            return False
        else:
            participants = Participation.objects \
                .filter(Q(frame=self) & Q(status="参加中"))

            return participants.count() >= self.upper_limit

    def is_closed(self):
        return timezone.now() > self.deadline

    def num_participants(self):
        status_query = Q(status="参加中")
        return self.participation_set.filter(status_query).count()

    def deadline_format(self):
        return self.deadline

    def participant_id_list(self):
        return self.participation_set.all().values_list('user', flat=True)

    def reserved_id_list(self):
        return self.participation_set \
                   .filter(status="参加中") \
                   .values_list('user', flat=True)

    def get_reserved_users(self):
        participations = self.participation_set.filter(status="参加中")
        return [p.user for p in participations]

    def waiting_id_list(self):
        return self.participation_set \
                   .filter(status="キャンセル待ち") \
                   .values_list('user', flat=True)

    def get_filled_rate(self):
        """Calculate participant capacity ratio.
        参加者上限数に対し、何%の応募があるかを返す。

        この関数は必ず何らかの整数値が返る事が期待されている。
        値が不明であることを明示する場合は、関数の呼び出し元で
        不明に対する処理を調整しなければならない。
        """
        participants = float(self.num_participants())
        limit = float(self.upper_limit)
        try:
            ratio = math.floor(participants * 100 / limit)
        except ZeroDivisionError:
            # XXX: zero division = 100%?
            ratio = 100

        return ratio


class Participation(AbstractBaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=30)
    frame = models.ForeignKey(Frame, blank=True, null=True)

    class Meta:
        unique_together = (('event', 'user'),)

    def __str__(self):
        return "Participant: %(username)s, Status: %(status)s" % {
            'username': self.user.username,
            'status': self.status,
        }

    def save(self, *args, **kwargs):
        return super(Participation, self).save(*args, **kwargs)


class Comment(AbstractBaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    reply_to = models.ForeignKey('self',
                                 on_delete=models.CASCADE,
                                 related_name='replies',
                                 null=True)

    def __str__(self):
        if self.reply_to:
            return ">> %s\n%s :\"%s" % (str(self.reply_to),
                                        self.user.username,
                                        self.text)
        else:
            return "%s: \"%s\"" % (self.user.username,
                                   self.text)

    def get_absolute_url(self):
        return reverse('event:detail', kwargs={'pk': self.event.id})

    def save(self, *args, **kwargs):
        return super(Comment, self).save(*args, **kwargs)


class Question(models.Model):
    event = models.ForeignKey(Event,
                              on_delete=models.CASCADE,
                              related_name='question')

    question = models.TextField()

    def __str__(self):
        return self.question


class Answer(AbstractBaseModel):
    question = models.ForeignKey(Question,
                                 on_delete=models.CASCADE,
                                 related_name='answer')

    participation = models.ForeignKey(Participation,
                                      on_delete=models.CASCADE,
                                      related_name='answer')

    text = models.TextField()

    def __str__(self):
        return "Q: " + self.question.question + " -> " + "A: " + self.text

    def save(self, *args, **kwargs):
        return super(Answer, self).save(*args, **kwargs)
