from django.contrib import admin
from .models import Event, EventAdmin, Participation, ParticipationAdmin
# Register your models here.

admin.site.register(Event, EventAdmin)
admin.site.register(Participation, ParticipationAdmin)