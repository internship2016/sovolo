# coding=utf-8
from django.utils import timezone
from django.db import models
from base.models import AbstractBaseModel
from django.contrib import admin

# Create your models here.


class Tag(AbstractBaseModel):
    name = models.CharField(max_length=100, unique=True)

    def save(self, *args, **kwargs):
        return super(Tag, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'modified')
