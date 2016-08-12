# coding=utf-8
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.urlresolvers import reverse
from django.conf import settings
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

    # regionは地方自治体コードで指定
    region = models.IntegerField(null=True)
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

    def save(self, *args, **kwargs):
        return super(User, self).save(*args, **kwargs)


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'created', 'modified')