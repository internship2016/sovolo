# coding=utf-8
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.urlresolvers import reverse
from django.conf import settings
from django.apps import apps

from datetime import datetime

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
    first_name = models.CharField(max_length=100,null=True)
    last_name = models.CharField(max_length=100,null=True)
    username = models.CharField(max_length=100,null=True)
    birthday = models.DateField(null=True)
    telephone = models.CharField(max_length=11, null=True)
    emergency_contact = models.CharField(max_length=11, null=True)
    email = models.EmailField(unique=True, db_index=True)
    sex = models.NullBooleanField()
    occupation = models.CharField(max_length=100, null=True)

    # regionは都道府県で指定
    prefectures = {
                "Hokkaido": "北海道",
                "Aomori": "青森県",
                "Iwate": "岩手県",
                "Miyagi": "宮城県",
                "Akita": "秋田県",
                "Yamagata": "山形県",
                "Fukushima": "福島県",
                "Ibaraki": "茨城県",
                "Tochigi": "栃木県",
                "Gunnma": "群馬県",
                "Saitama": "埼玉県",
                "Chiba": "千葉県",
                "Tokyo": "東京都",
                "Kanagawa": "神奈川県",
                "Niigata": "新潟県",
                "Toyama": "富山県",
                "Ishikawa": "石川県",
                "Fukui": "福井県",
                "Yamanashi": "山梨県",
                "Nagano": "長野県",
                "Gifu": "岐阜県",
                "Shizuoka": "静岡県",
                "Aichi": "愛知県",
                "Mie": "三重県",
                "Shiga": "滋賀県",
                "Kyoto": "京都府",
                "Osaka": "大阪府",
                "Hyogo": "兵庫県",
                "Nara": "奈良県",
                "Wakayama": "和歌山県",
                "Tottori": "鳥取県",
                "Shimane": "島根県",
                "Okayama": "岡山県",
                "Hiroshima": "広島県",
                "Yamaguchi": "山口県",
                "Tokushima": "徳島県",
                "Kagawa": "香川県",
                "Ehime": "愛媛県",
                "Kouchi": "高知県",
                "Fukuoka": "福岡県",
                "Saga": "佐賀県",
                "Nagasaki": "長崎県",
                "Kumamoto": "熊本県",
                "Ooita": "大分県",
                "Miyazaki": "宮崎県",
                "Kagoshima": "鹿児島県",
                "Okinawa": "沖縄県"
    }

    region_list = ((key, value) for key, value in prefectures.items())
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

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

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

    def get_participating_events(self):
        Participation = apps.get_model('event', 'Participation')
        #print(Participation.objects.values_list('event', flat=True).filter(user=self), file=sys.stderr)
        events = [participation.event for participation in Participation.objects.filter(user=self)]
        return events

    def save(self, *args, **kwargs):
        return super(User, self).save(*args, **kwargs)


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'created', 'modified')