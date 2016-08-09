from django.contrib import admin
from .models import Group, GroupAdmin


admin.site.register(Group, GroupAdmin)
