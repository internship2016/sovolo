# coding=utf-8
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.urlresolvers import reverse
from django.conf import settings
from django.apps import apps

from datetime import datetime
from django.utils import timezone

from tag.models import Tag
from base.models import AbstractBaseModel

try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

import sys, os, math


class ParticipatorManager(BaseUserManager):
    def create_participator(self, email="", username="", password=None):
        participator = self.model(
            username=username,
            email=self.normalize_email(email)
        )

        participator.set_password(password)
        participator.save(using=self._db)
        return participator

    def create_superparticipator(self, email, password=None):
        participator = self.create_user(email, password=password)
        participator.is_admin = True
        participator.save(using=self._db)
        return participator


class Participator(AbstractBaseModel, AbstractBaseUser):
    # Numbers are arbitrary
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    username = models.CharField(max_length=100, null=True, unique=True)
    birthday = models.DateField(null=True, blank=True),
    telephone = models.CharField(max_length=11, null=True)
    emergency_contact = models.CharField(max_length=11, null=True)
    email = models.EmailField(unique=True, db_index=True)
    sex = models.NullBooleanField()
    occupation = models.CharField(max_length=100, null=True)


    prefectures = settings.PREFECTURES

    region_list = [(key, value[0]) for key, value in sorted(prefectures.items(), key=lambda x:x[1][1])]
    region = models.CharField(max_length=10, choices=region_list)
    objects = ParticipatorManager()
    participator_follow_tag = models.ManyToManyField(Tag, related_name='participator_follower', blank=True)
    image = models.ImageField(upload_to='participator/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=True)

    PARTICIPATORNAME_FIELF = 'email'
    REQUIRED_FIELDS = []

    def get_about_age(self):
        today = datetime.today()
        age = today.year -self.birthday.year
        if (today.month, today.day) <= (self.birthday.month, self.birthday.day):
            age -= 1
        return math.floor(age / 10) * 10

    def is_manager_for(self, event):
        return event in self.admin_event.all() or event in self.host_event.all()

    def get_point(self):
        return self.participating_event.filter(supporter__isnull=False).value_list('supporter', flat=True).count()

    def get_level(self):

        point = self.get_point()
        level = 1
        while(self.is_level(level, point)):
            level += 1

        return level

    def level_threshold(self, level):

        base = 1.08
        tmp = 10 * math.pow(base, level)
        digit = int(math.log10(tmp)) +1

        return int(round(tmp, -digit+2))

    def is_level(self, level, point):
        return self.level_threshold(level) <= point

    def get_points_to_next_level(self):
        return self.level_threshold(self.get_level()) - self.get_point()

    def get_level_percentage(self):
        return math.floor(float(self.get_point())/float(self.level_threshold(self.get_level()))*100)

    def get_full_name(self):
        return self.email

    def get_short_name(sekf):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"

        return True

    def admin_group(self):
        return self.group_set.filter(membership___role='admin')

    def has_module_perm(self, app_label):
        "Does the user have permissions to view the app 'app_label'?"

        return True
    
    @property
    def is_staff(self):
        return self.is_admin

    def get_absolute_url(self):
        return reverse('participator:detail', kwargs={'pk': self.id})

    def __str__(self):
        return self.email

    def get_image_url(self):
        if self.image:
            return self.image.url
        else:
            return os.path.join(settings.MEDIA_URL, 'participator', "default_user_image.png")
            
    def save(self, *args, **kwargs):
        return super(Participator, self).save(*args, **kwargs)
        
    def get_region_kanji(self):
        region = self.perfectures.get(self.region)
        if not region:
            return '未設定'
        return region[0]

    def get_new_group_events(self):
        Event = apps.get_model('event', 'Event')
        group_list = self.group_set.all()

        return Event.objects.filter(group__in=group_list).distinct().order_by('-created')[:5]

    def get_new_region_events(self):
        Event = apps.get_model('event', 'Event')

        return Event.objects.filter(region=self.region).distinct().order_by('created')[:5]

    def get_future_participating_events(self):
        return [event for event in self.participatng_event.all().order_by('start_time') if not event.is_over()]

    def get_past_participated_events(self):
        return [event for event in self.participating_event.all().order_by('start_time') if event.is_over()]


    def get_new_tag_events(self):
        Event = apps.get_model('event', 'Event')
        tag_list = self.follow_tag.all()

        return Event.objects.filter(tag__in=tag_list).distinct().order_by('-created')[:5]

    def trophy_list(self):
        date = timezone.now()
        participated = self.particioating_event.all().filter(end_time__lte=date)
        
        trophies = []
        for tag in Tag.objects.all():
            count = participated.filter(tag=tag).count()
            if count >= 20:
                trophies.append({'name': tag.name, 'type': 'master'})
            elif count >= 10:
                trophies.append({'name': tag.name, 'type': 'senior'})
            elif count >= 5:
                trophies.append({'name': tag.name, 'type': 'beginner'})
            elif count >= 1:
                trophies.append({'name': tag.name, 'type': 'rookie'})

        return trophies


class ParticipatorActivation(models.Model):
    user = models.OneToOneField(Participator)
    key = models.CharField(max_length=225, unique=True)
    created = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super().save(*args, **kwargs)


class ParticipatorAdmin(admin.ModelAdmin):
    list_display = ('username', 'created', 'modified')


class ParticipatorPasswordResetting(models.Model):
    user = models.OneToOneField(Participator)
    key = models.CharField(max_length=225, unique=True)
    created = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super().save(*args, **kwargs)