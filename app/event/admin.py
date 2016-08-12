from django.contrib import admin
from .models import Event, EventAdmin, Participation, ParticipationAdmin, Frame, FrameAdmin, Comment, Question, Answer
# Register your models here.

admin.site.register(Event, EventAdmin)
admin.site.register(Participation, ParticipationAdmin)
admin.site.register(Frame, FrameAdmin)
admin.site.register(Comment)
admin.site.register(Question)
admin.site.register(Answer)