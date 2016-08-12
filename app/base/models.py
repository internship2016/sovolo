# coding=utf-8
from django.utils import timezone
from django.db import models
import sys

from PIL import Image
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile


class AbstractBaseModel(models.Model):
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField(null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # On save, update timestamps
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()

        width = 500
        height = 500
        if hasattr(self, 'image') and self.image:
            img_file = Image.open(StringIO(self.image.read()))
            (imw, imh) = img_file.size
            if (imw > width) or (imh > height):
                #change size of image to fit within boudaries specified by width and height
                img_file.thumbnail((width, height), Image.ANTIALIAS)

            if img_file.mode == "RGBA":
                img_file.load()
                background = Image.new("RGB", img_file.size, (255, 255, 255))
                background.paste(img_file, mask=img_file.split()[3])  # 3 is alpha channel
                img_file = background

            output = StringIO()
            img_file.convert('RGB').save(output, format='JPEG', quality=60)
            output.seek(0)
            self.image = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.image.name.split('.')[0],
                                              'image/jpeg', sys.getsizeof(output), None)

        return super(AbstractBaseModel, self).save(*args, **kwargs)
