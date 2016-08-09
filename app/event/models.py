# coding=utf-8
from django.utils import timezone

from django.db import models
from django.core.urlresolvers import reverse
from user.models import User
from django.contrib.auth.models import User as DjangoUser

from PIL import Image
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

# Create your models here.

class Event(models.Model):
    #Numbers are arbitrary
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    meeting_place = models.CharField(max_length=400)
    place = models.CharField(max_length=400)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    image = models.ImageField(upload_to='events/')
    contact = models.CharField(max_length=200)
    details = models.TextField()
    notes = models.TextField(blank=True)
    ticket = models.BooleanField()
    hashtag = models.CharField(max_length=100, blank=True)
    share_message = models.CharField(max_length=100, blank=True)
    host_user = models.ForeignKey(DjangoUser, related_name='host_event')
    #regionは地方自治体コードで指定
    region = models.IntegerField()

    participant = models.ManyToManyField(User, through='Participation', blank=True)
    admin = models.ManyToManyField(User, related_name='admin_event', blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('event:detail', kwargs={'event_id': self.id})

    def save(self, *args, **kwargs):
        # On save, update timestamps
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()

        #image processing
        width = 500
        height = 500
        if self.image:
            img_file = Image.open(StringIO(self.image.read()))
            (imw, imh) = img_file.size
            if (imw > width) or (imh > height):
                img_file.thumbnail((width, height), Image.ANTIALIAS)

            if img_file.mode == "RGBA":
                img_file.load()
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])  # 3 is alpha channel
                img_file = background

            output = StringIO()
            img_file.convert('RGB').save(output, format='JPEG', quality = 60)
            output.seek(0)
            self.image = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.image.name.split('.')[0], 'image/jpeg', sys.getsizeof(output), None)

        try:
            this = Event.objects.get(id=self.id)
            if this.photo != self.photo:
                this.photo.delete(save=False)
        except: pass

        return super(Event, self).save(*args, **kwargs)

class Frame(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    description = models.TextField(default='通常参加枠')
    lower_limit = models.IntegerField(blank=True)
    upper_limit = models.IntegerField(blank=True)
    deadline = models.DateTimeField()
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField()

    def save(self, *args, **kwargs):
        # On save, update timestamps
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Frame, self).save(*args, **kwargs)


class Participation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10)
    created = models.DateTimeField(editable=False)
    frame = models.ForeignKey(Frame)
    modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        # On save, update timestamps
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Participation, self).save(*args, **kwargs)

class Comment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField()

    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies')

    def save(self, *args, **kwargs):
        # On save, update timestamps
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Comment, self).save(*args, **kwargs)

class Question(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='question')
    question = models.TextField()

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer')

    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField()

    def save(self, *args, **kwargs):
        # On save, update timestamps
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Answer, self).save(*args, **kwargs)