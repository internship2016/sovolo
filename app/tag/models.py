# coding=utf-8
from django.utils import timezone
from django.db import models

# Create your models here.

class Tag(models.Model):
    tag = models.CharField(max_length=100)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        # On save, update timestamps
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Tag, self).save(*args, **kwargs)