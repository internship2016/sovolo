# coding=utf-8
from django.utils import timezone
from django.db import models
from user.models import User
from event.models import Event

from PIL import Image
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
# Create your models here.

class Group(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    image = models.ImageField(upload_to='group/', blank=True)

    event = models.ManyToManyField(Event, blank=True)

    member = models.ManyToManyField(User)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # On save, update timestamps
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()

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
            img_file.convert('RGB').save(output, format='JPEG', quality=60)
            output.seek(0)
            self.image = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.image.name.split('.')[0],
                                              'image/jpeg', sys.getsizeof(output), None)

        try:
            this = Event.objects.get(id=self.id)
            if this.photo != self.photo:
                this.photo.delete(save=False)
        except:
            pass

        return super(Group, self).save(*args, **kwargs)

class Membership(models.Model):
    member = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    role = models.CharField(max_length=20, default='Normal')