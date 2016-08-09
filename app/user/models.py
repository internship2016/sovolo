# coding=utf-8
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import sys

from tag.models import Tag
from base.models import AbstractBaseModel

from PIL import Image
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError
        user = self.model(
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
    nickname = models.CharField(max_length=100,null=True)
    birthday = models.DateField(null=True)
    telephone = models.CharField(max_length=11, null=True)
    emergency_contact = models.CharField(max_length=11, null=True)
    email = models.EmailField(unique=True, db_index=True)
    occupation = models.CharField(max_length=100, null=True)

    # regionは地方自治体コードで指定
    region = models.IntegerField(null=True)
    follow_tag = models.ManyToManyField(Tag, related_name='follower', blank=True)
    image = models.ImageField(upload_to='users/', null=True)

    objects = UserManager()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

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

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        return super(User, self).save(*args, **kwargs)
