from django.contrib import admin
from .models import User, UserReviewList, Skill, UserComment

# Register your models here.
# class ChoiceInline(admin.StackedInline):


class UserReviewListInline(admin.TabularInline):
    model = UserReviewList
    fk_name = "to_rate_user"
    readonly_fields = ('post_day',)
    extra = 3

class SkillAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'skilltodo',
    )

class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'created', 'modified')
    inlines = [UserReviewListInline]

class UserCommentAdmin(admin.ModelAdmin):
    model = UserComment
    extra = 3

admin.site.register(User, UserAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(UserComment,UserCommentAdmin)
