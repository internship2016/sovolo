# coding=utf-8
from django.utils import timezone
from django.db import models
import sys

from tag.models import Tag

# Create your models here.

class User(models.Model):

    # Numbers are arbitrary
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    password = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100)
    birthday = models.DateField()
    telephone = models.CharField(max_length=11, blank=True)
    emergency_contact = models.CharField(max_length=11, blank=True)
    email = models.CharField(max_length=200)
    occupation = models.CharField(max_length=100, blank=True)
    # regionは地方自治体コードで指定
    region = models.IntegerField()
    fb_access_token = models.CharField(max_length=100, blank=True)
    twitter_access_token = models.CharField(max_length=100, blank=True)
    follow_tag = models.ManyToManyField(Tag, related_name='follower', blank=True)
    image = models.ImageField(upload_to='users/', blank=True)

    def __str__(self):
        return self.nickname

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
                #change size of image to fit within boudaries specified by width and height
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

        return super(User, self).save(*args, **kwargs)
