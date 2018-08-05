from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from django.shortcuts import redirect
# from django.shortcuts import HttpResponse
from social.exceptions import AuthCanceled

class AuthCanceledExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if type(exception) == AuthCanceled:
            return redirect('/')
        else:
            pass
