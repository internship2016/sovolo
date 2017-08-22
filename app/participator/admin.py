from django.contrib import admin
from .models import Participator, ParticipatorAdmin

admin.site.register(Participator, ParticipatorAdmin)
