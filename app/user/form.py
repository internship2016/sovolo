from django import forms
from user.models import UserReviewList



class UserReviewListForm(forms.ModelForm):

    class Meta():
        model = UserReviewList
        fields = ('rating','comment')
        # widgets = {
        #     'comment': forms.Textarea(attrs={'cols': 20, 'rows': 10}),
        # }
