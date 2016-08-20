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
    prefectures = {
        "Hokkaido": ("北海道", 1),
        "Aomori": ("青森県", 2),
        "Iwate": ("岩手県", 3),
        "Miyagi": ("宮城県", 4),
        "Akita": ("秋田県", 5),
        "Yamagata": ("山形県", 6),
        "Fukushima": ("福島県", 7),
        "Ibaraki": ("茨城県", 8),
        "Tochigi": ("栃木県", 9),
        "Gunnma": ("群馬県", 10),
        "Saitama": ("埼玉県", 11),
        "Chiba": ("千葉県", 12),
        "Tokyo": ("東京都", 13),
        "Kanagawa": ("神奈川県", 14),
        "Niigata": ("新潟県", 15),
        "Toyama": ("富山県", 16),
        "Ishikawa": ("石川県", 17),
        "Fukui": ("福井県", 18),
        "Yamanashi": ("山梨県", 19),
        "Nagano": ("長野県", 20),
        "Gifu": ("岐阜県", 21),
        "Shizuoka": ("静岡県", 22),
        "Aichi": ("愛知県", 23),
        "Mie": ("三重県", 24),
        "Shiga": ("滋賀県", 25),
        "Kyoto": ("京都府", 26),
        "Osaka": ("大阪府", 27),
        "Hyogo": ("兵庫県", 28),
        "Nara": ("奈良県", 29),
        "Wakayama": ("和歌山県", 30),
        "Tottori": ("鳥取県", 31),
        "Shimane": ("島根県", 32),
        "Okayama": ("岡山県", 33),
        "Hiroshima": ("広島県", 34),
        "Yamaguchi": ("山口県", 35),
        "Tokushima": ("徳島県", 36),
        "Kagawa": ("香川県", 37),
        "Ehime": ("愛媛県", 38),
        "Kouchi": ("高知県", 39),
        "Fukuoka": ("福岡県", 40),
        "Saga": ("佐賀県", 41),
        "Nagasaki": ("長崎県", 42),
        "Kumamoto": ("熊本県", 43),
        "Ooita": ("大分県", 44),
        "Miyazaki": ("宮崎県", 45),
        "Kagoshima": ("鹿児島県", 46),
        "Okinawa": ("沖縄県", 47)
    }

    region_list = [(key, value[0]) for key, value in sorted(prefectures.items(), key=lambda x:x[1][1])]
    region = models.CharField(max_length=10, choices=region_list)
    follow_tag = models.ManyToManyField(Tag, related_name='follower', blank=True)
    image = models.ImageField(upload_to='users/', null=True, blank=True)
    objects = UserManager()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_about_age(self):
        today = datetime.today()
        age = today.year - self.birthday.year
        if (today.month, today.day) <= (self.birthday.month, self.birthday.day):
            age -= 1
        return math.floor(age / 10) * 10

    def is_manager_for(self, event):
        return event in self.admin_event.all() or event in self.host_event.all()

    def get_point(self):
        return self.participating_event.filter(supporter__isnull=False).values_list('supporter', flat=True).count() 

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
            return os.path.join(settings.MEDIA_URL, 'users/', "default_user_image.jpg")

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

        return Event.objects.filter(group__in=group_list).distinct().order_by('-created')[:5]

    def get_new_region_events(self):
        Event = apps.get_model('event', 'Event')

        return Event.objects.filter(region=self.region).distinct().order_by('-created')[:5]

    def get_future_participating_events(self):
        date = timezone.now()
        return self.participating_event.all().filter(start_time__gte=date).order_by('start_time')

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
                trophies.append({'name': tag.name, 'type': 'trophy-master'})
            elif count >= 10:
                trophies.append({'name': tag.name, 'type': 'trophy-senior'})
            elif count >= 3:
                trophies.append({'name': tag.name, 'type': 'trophy-beginner'})
            elif count >= 1:
                trophies.append({'name': tag.name, 'type': 'trophy-rookie'})

        return trophies


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'created', 'modified')
