from django.contrib import admin
from .models import Tag, TagAdmin

# Register your models here.

admin.site.register(Tag, TagAdmin)
