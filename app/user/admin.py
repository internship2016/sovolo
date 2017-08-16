from django.contrib import admin
from .models import User, UserReviewList
# Register your models here.

# class ChoiceInline(admin.StackedInline):
class UserReviewListInline(admin.TabularInline):
    model = UserReviewList
    extra = 3

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'created', 'modified')
    inlines = [UserReviewListInline]

admin.site.register(User, UserAdmin)
