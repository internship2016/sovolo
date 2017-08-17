from django.contrib import admin
from .models import Event, Frame, Participation, Question, Answer, Comment
# Register your models here.


class ParticipationInline(admin.TabularInline):
    model = Participation
    extra = 1

class FrameInline(admin.TabularInline):
    model = Frame
    extra = 1

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1


class QuestionAdmin(admin.ModelAdmin):
    model = Question
    inlines = (AnswerInline,)

class EventAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'created', 'modified', 'get_tags_as_string')
    inlines = [ParticipationInline, FrameInline, CommentInline]


admin.site.register(Event, EventAdmin)
admin.site.register(Question, QuestionAdmin)
