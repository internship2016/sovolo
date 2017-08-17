from django.contrib import admin
from .models import User, UserReviewList
# Register your models here.
from .models import Frame, FrameAdmin
# class ChoiceInline(admin.StackedInline):
class UserReviewListInline(admin.TabularInline):
    model = UserReviewList
    fk_name = "to_rate_user"
    extra = 3

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'created', 'modified')
    inlines = [UserReviewListInline]

admin.site.register(User, UserAdmin)
admin.site.register(Frame,FrameAdmin)
