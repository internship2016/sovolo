from django import forms
from user.models import UserReviewList


class UserReviewListForm(forms.ModelForm):

    class Meta():
        model = UserReviewList
        fields = ('rating', 'comment')
