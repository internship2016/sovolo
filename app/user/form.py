from django import forms
from user.models import UserReviewList, UserComment, Skill


class UserReviewListForm(forms.ModelForm):

    class Meta():
        model = UserReviewList
        fields = ('rating', 'comment')

class UserCommentCreateForm(forms.ModelForm):

    class Meta():
        model = UserComment
        fields = ('text',)

class SkillForm(forms.ModelForm):

    class Meta():
        model = Skill
        fields = ('skilltodo', 'tag')
