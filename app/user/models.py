# coding=utf-8
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.urlresolvers import reverse
from django.conf import settings
from django.apps import apps

from django.utils.translation import ugettext_lazy as _

from datetime import datetime
from django.utils import timezone

from tag.models import Tag
from base.models import AbstractBaseModel

import os
import math

# review
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class UserManager(BaseUserManager):
    def create_user(self, email="", username="", password=None):
        user = self.model(
            username=username,
            email=self.normalize_email(email)
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseModel, AbstractBaseUser):
    # Numbers are arbitrary
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    username = models.CharField(max_length=100, null=True, unique=True)
    birthday = models.DateField(null=True, blank=True)
    telephone = models.CharField(max_length=11, null=True)
    emergency_contact = models.CharField(max_length=11, null=True)
    email = models.EmailField(unique=True, db_index=True)
    sex = models.NullBooleanField()  # True:Men, False:Women
    occupation = models.CharField(max_length=100, null=True)

    # regionは都道府県で指定
    # XXX: dup
    prefectures = settings.PREFECTURES
    prefs = prefectures.items()
    prefs = sorted(prefs, key=lambda x: x[1][1])
    region_list = [(k, v[0]) for k, v in prefs]

    region = models.CharField(max_length=10, choices=region_list)

    follow_tag = models.ManyToManyField(Tag,
                                        related_name='follower',
                                        blank=True)

    image = models.ImageField(upload_to='users/', null=True, blank=True)
    objects = UserManager()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    language = models.CharField(verbose_name=_('Language'),
                                max_length=10,
                                choices=settings.LANGUAGES,
                                default=settings.LANGUAGE_CODE,  # FIXME: !!
                                null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_about_age(self):
        today = datetime.today()
        birthday = self.birthday
        age = today.year - birthday.year

        if (today.month, today.day) <= (birthday.month, birthday.day):
            age -= 1

        return math.floor(age / 10) * 10

    def is_manager_for(self, event):
        if event in self.admin_event.all():
            return True

        if event in self.host_event.all():
            return True

        return False

    def get_point(self):
        return self.participating_event \
                   .filter(supporter__isnull=False) \
                   .values_list('supporter', flat=True) \
                   .count()

    def get_level(self):
        point = self.get_point()
        level = 1

        # FIXME: Deterministic, this shouldn't be using while statement
        while(self.is_level(level, point)):
            level += 1

        return level

    def level_threshold(self, level):
        # 有効数字2桁
        base = 1.08
        tmp = 10 * math.pow(base, level)
        digit = int(math.log10(tmp)) + 1

        return int(round(tmp, -digit + 2))

    def is_level(self, level, point):
        return self.level_threshold(level) <= point

    def get_points_to_next_level(self):
        return self.level_threshold(self.get_level()) - self.get_point()

    def get_level_percentage(self):
        point = float(self.get_point())
        threshold = float(self.level_threshold(self.get_level()))
        return math.floor(point * 100 / threshold)

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def admin_group(self):
        return self.group_set.filter(membership__role='admin')

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def get_absolute_url(self):
        return reverse('user:detail', kwargs={'pk': self.id})

    def __str__(self):
        return self.email

    def get_image_url(self):
        if self.image:
            return self.image.url
        else:
            return os.path.join(settings.MEDIA_URL,
                                'users/',  # FIXME: trailing slash?
                                "default_user_image.png")

    def save(self, *args, **kwargs):
        return super(User, self).save(*args, **kwargs)

    def get_region_kanji(self):
        region = self.prefectures.get(self.region)
        if not region:
            return '未設定'  # XXX: regionがこない場合は未設定でいいのか
        return region[0]

    def get_new_group_events(self):
        Event = apps.get_model('event', 'Event')
        group_list = self.group_set.all()

        return Event.objects \
                    .filter(group__in=group_list) \
                    .distinct() \
                    .order_by('-created')[:5]

    def get_new_region_events(self):
        Event = apps.get_model('event', 'Event')

        events = Event.objects \
                      .filter(region=self.region) \
                      .distinct() \
                      .order_by('-created')

        # TODO: Consider using 'filter()' to return an iterator
        return [event for event in events if not event.is_over()]

    def get_future_participating_events(self):
        events = self.participating_event \
                     .all() \
                     .order_by('start_time')
        return [event for event in events if not event.is_over()]

    def get_past_participated_events(self):
        return [event for event in self.participating_event.all().order_by('start_time') if event.is_over()]


    def get_new_tag_events(self):
        Event = apps.get_model('event', 'Event')
        tag_list = self.follow_tag.all()

        return Event.objects.filter(tag__in=tag_list).distinct().order_by('-created')[:5]

    def trophy_list(self):
        date = timezone.now()
        participated = self.participating_event.all().filter(end_time__lte=date)

        trophies = []
        for tag in Tag.objects.all():
            count = participated.filter(tag=tag).count()
            if count >= 20:
                trophies.append({'name': tag.name, 'type': 'master'})
            elif count >= 10:
                trophies.append({'name': tag.name, 'type': 'senior'})
            elif count >= 3:
                trophies.append({'name': tag.name, 'type': 'beginner'})
            elif count >= 1:
                trophies.append({'name': tag.name, 'type': 'rookie'})

        return trophies

    # shuto tsuchiya
    def get_mean_rating(self):
        return self.to_rate_user.aggregate(Avg('rating'))['rating__avg']


class UserActivation(models.Model):
    user = models.OneToOneField(User)
    key = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super().save(*args, **kwargs)


class UserPasswordResetting(models.Model):
    user = models.OneToOneField(User)
    key = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super().save(*args, **kwargs)


class UserReviewList(models.Model):

    to_rate_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='to_rate_user',
        )

    rating = models.IntegerField(validators=[MinValueValidator(0),
                                       MaxValueValidator(5)])

    comment = models.CharField(max_length=200, null=True)

    from_rate_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='from_rate_user',
        )

    joined_event = models.ForeignKey('event.Event', null=True)

    # post_day = models.DateTimeField(default=timezone.now, editable=False, null=True)
    post_day = models.DateTimeField(default=timezone.now, null=True)
    def __str__(self):
        # Built-in attribute of django.contrib.auth.models.User !
        return str(self.to_rate_user)
