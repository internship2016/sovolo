# coding=utf-8
from django.utils import timezone
from django.db import models
from base.models import AbstractBaseModel

# Create your models here.

class Tag(AbstractBaseModel):
    tag = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        return super(Tag, self).save(*args, **kwargs)