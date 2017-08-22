from django.shortcuts import redirect
from social.pipeline.partial import partial
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
import uuid
import urllib


@partial
def get_profile_image(strategy, details, response,
                      user=None, is_new=False, *args, **kwargs):
    backend = kwargs.get('backend')
    if is_new:
        if backend.name == 'facebook':
            url = "http://graph.facebook.com/%s/picture?type=large" % response['id']
        elif backend.name == 'twitter':
            url = response.get('profile_image_url', '').replace('_normal', '')
        if url:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urllib.request.urlopen(url).read())
            img_temp.flush()

            user.image.save(str(uuid.uuid4()), File(img_temp))
            pass


@partial
def require_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    backend = kwargs.get('backend')
    if user and user.email:
        # The user we're logging in already has their email attribute set
        return
    elif is_new and not details.get('email'):
        # If we're creating a new user, and we can't find the email in the
        # details.  we'll attempt to request it from the data returned from our
        # backend strategy
        userEmail = strategy.request_data().get('email')
        if userEmail:
            details['email'] = userEmail
        else:
            # If there's no email information to be had, we need to ask the
            # user to fill it in.  This should redirect us to a view
            return redirect('/user/email_required')
