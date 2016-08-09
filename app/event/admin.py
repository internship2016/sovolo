from django.contrib import admin
from .models import Event, EventAdmin
# Register your models here.

admin.site.register(Event, EventAdmin)