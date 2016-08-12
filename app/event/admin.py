from django.contrib import admin
from .models import Answer
from .models import Comment
from .models import Event
from .models import EventAdmin
from .models import Frame
from .models import FrameAdmin
from .models import Participation
from .models import ParticipationAdmin
from .models import Question
# Register your models here.

admin.site.register(Event, EventAdmin)
admin.site.register(Participation, ParticipationAdmin)
admin.site.register(Frame, FrameAdmin)
admin.site.register(Comment)
admin.site.register(Question)
admin.site.register(Answer)
