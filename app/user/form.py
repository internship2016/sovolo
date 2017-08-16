from django import forms
from user.models import UserReviewList


class UserReviewListForm(forms.ModelForm):
    class Meta():
        model = UserReviewList
        # fields = ('rating','comment')
        fields = ('rated_user','rating','comment')

    def send_email(self):
        # send email using the self.cleaned_data dictionary
        pass
