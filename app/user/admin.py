from django.contrib import admin
from .models import User, UserReviewList, Skill

# Register your models here.
# class ChoiceInline(admin.StackedInline):


class UserReviewListInline(admin.TabularInline):
    model = UserReviewList
    fk_name = "to_rate_user"
    readonly_fields = ('post_day',)
    extra = 3

# class SkillAdmin(admin.ModelAdmin):
#     list_display = (
#         'pk',
#         'description',
#         'skilltodo',
#     )

class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'created', 'modified')
    inlines = [UserReviewListInline]


admin.site.register(User, UserAdmin)
# admin.site.register(Skill, SkillAdmin)
