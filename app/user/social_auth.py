from django.shortcuts import redirect
from social.pipeline.partial import partial
from social.pipeline.user import USER_FIELDS


@partial
def require_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    backend = kwargs.get('backend')
    if user and user.email:
        return  # The user we're logging in already has their email attribute set
    elif is_new and not details.get('email'):
        # If we're creating a new user, and we can't find the email in the details
        # we'll attempt to request it from the data returned from our backend strategy
        userEmail = strategy.request_data().get('email')
        if userEmail:
            details['email'] = userEmail
        else:
            # If there's no email information to be had, we need to ask the user to fill it in
            # This should redirect us to a view
            return redirect('/user/email_required')