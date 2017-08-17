`from django.contrib import admin
from .models import Answer
from .models import Comment
from .models import Event, Frame, Participation, Question
# Register your models here.

class EventAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'created', 'modified', 'get_tags_as_string')


class ParticipationAdmin(admin.ModelAdmin):
    list_display = ['pk', 'event', 'user', 'status', 'frame']


class FrameAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'event',
        'description',
        'upper_limit',
        'deadline',
    )


admin.site.register(Event, EventAdmin)
admin.site.register(Participation, ParticipationAdmin)
admin.site.register(Frame, FrameAdmin)
admin.site.register(Comment)
admin.site.register(Question)
admin.site.register(Answer)
`
