from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic import DetailView, View, ListView
from django.contrib import messages
from django.shortcuts import get_object_or_404
from tag.models import Tag
from base.utils import send_template_mail
from django.contrib.auth import views as auth_views
import uuid
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.utils.decorators import method_decorator
from django.utils import timezone
from .models import User, Skill, UserActivation, UserPasswordResetting, UserReviewList
from .form import UserReviewListForm
from django.urls import reverse
from django.contrib.auth.mixins import UserPassesTestMixin

from django.utils import timezone
from django.forms import formset_factory
from event.models import Event

from django.utils import translation
from django.conf import settings

from django.utils.translation import ugettext_lazy as _


class UserCreateView(CreateView):
    model = User
    fields = ['email', 'password', 'username']
    template_name = 'user/register.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.is_active = False
        user.save()

        activation_key = self.create_activation_key()
        activation = UserActivation(user=user, key=activation_key)
        activation.save()

        base_url = "/".join(self.request.build_absolute_uri().split("/")[:3])

        activation_url = "{0}/user/activation/{1}".format(base_url,
                                                          activation_key)

        send_template_mail(
            "email/activation.txt",
            {"activation_url": activation_url},
            "Sovol Info <info@sovol.earth>",
            [user.email],
        )

        info_msg = _("Confirmation email has been sent to your email address.") % {
            'email': user.email,
        }
        messages.info(self.request, info_msg)
        return redirect("top")

        key = uuid.uuid4().hex
        return key

    def get_form(self):
        from django import forms
        form = super().get_form()
        form.fields['password'].widget = forms.PasswordInput()
        form.fields['username'].maxlength = 15
        form.fields['username'].label = _("Username（Up to 15 characters)")
        return form


class UserActivationView(View):
    def get(self, request, *args, **kwargs):
        activation = get_object_or_404(UserActivation, key=kwargs['key'])
        user = activation.user
        user.is_active = True
        user.save()
        login(request, user, "django.contrib.auth.backends.ModelBackend")
        messages.info(request, _("You have successfully registered!"))
        return redirect("top")


class RequestPasswordReset(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user/request_password_reset.html')

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        user = User.objects.filter(email=email)
        if user.exists():
            user = user.first()
            reset_key = self.create_reset_key()

            if hasattr(user, "userpasswordresetting"):
                user.userpasswordresetting.key = reset_key
                user.userpasswordresetting.save()
            else:
                UserPasswordResetting(user=user, key=reset_key).save()

            # XXX: What does 3 mean?
            # XXX: os.path?
            absolute_uri = self.request.build_absolute_uri()
            base_url = "/".join(absolute_uri.split("/")[:3])

            reset_url = "{0}/user/reset_password/{1}".format(base_url,
                                                             reset_key)

            send_template_mail(
                "email/reset_password.txt",
                {"reset_url": reset_url},
                "Sovol Info<info@sovol.earth>",
                [user.email]
            )

        info_msg = _("A password reset was requested."
                     "If the email address is registered, "
                     "URL for resetting your password will be sent.")

        messages.info(request, info_msg)
        return redirect("top")

    def create_reset_key(self):
        key = uuid.uuid4().hex
        return key


class ResetPassword(View):
    def get(self, request, *args, **kwargs):
        resetting = UserPasswordResetting.objects.filter(key=kwargs['key'])
        if not resetting.exists():
            messages.error(request, _("Invalid URL"))
            return redirect("top")
        else:
            return render(request, 'user/reset_password.html')

    def post(self, request, *args, **kwargs):
        password = request.POST.get('password')

        resetting = UserPasswordResetting.objects.filter(key=kwargs['key'])
        if resetting .exists():
            resetting = resetting .first()
        else:
            messages.error(request, _("Failed to reset your password."))
            return redirect("top")

        user = resetting.user
        user.set_password(password)
        user.save()
        login(request, user, "django.contrib.auth.backends.ModelBackend")

        messages.info(request, _("Your new password has been set."))
        return redirect("top")


class UserDetailView(DetailView):
    template_name = 'user/detail.html'
    model = User
    context_object_name = 'user'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            messages.error(request, _("No user found"))
            return redirect('top')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        return context


class UserEditView(UpdateView):
    model = User
    fields = [
        'username',
        'email',
        'image',
        'region',
        'sex',
        'birthday',
        'language',
    ]

    template_name = 'user/edit.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(UserEditView, self).get_context_data(**kwargs)
        context['all_tags'] = Tag.objects.all
        context['languages'] = settings.LANGUAGES
        return context

    def form_valid(self, form):
        user = form.save(commit=False)

        new_tags = set([int(t) for t in self.request.POST.getlist('tags')])
        old_tags = set([t.id for t in user.follow_tag.all()])

        for tag_id in new_tags - old_tags:
            user.follow_tag.add(tag_id)

        for tag_id in old_tags - new_tags:
            user.follow_tag.remove(tag_id)

        self.request.session[translation.LANGUAGE_SESSION_KEY] = user.language

        messages.info(self.request, _("User profile was successfully edited."))
        return super(UserEditView, self).form_valid(form)


class AcquireEmail(View):
    def get(self, request, *args, **kwargs):
        """
        Request email for the create user flow for logins that don't specify
        their email address.
        """
        backend = request.session['partial_pipeline']['backend']
        return render(request, 'user/acquire_email.html', {"backend": backend})


def logout(request):
    messages.info(request, _("You have been successfully logged out."))
    return auth_views.logout(request, next_page="/")


# Review
class UserReviewView(DetailView):
    model = User
    template_name = 'user/user_review.html'


class UserPostReviewView(FormView):
    template_name = 'user/user_post_review.html'
    form_class = UserReviewListForm
    model = User

    def get_context_data(self, **kwargs):

        context = super(UserPostReviewView, self).get_context_data(**kwargs)
        if 'event_id' in self.request.GET:
            joined_event = Event.objects.get(pk=self.request.GET['event_id'])
            context['review_event'] = joined_event
        if 'to_user_id' in self.request.GET:
            to_user = User.objects.get(pk=self.request.GET['to_user_id'])
            context['to_user'] = to_user
        return context

    def form_valid(self, form):

        if 'event_id' in self.request.GET:
            joined_event = Event.objects.get(pk=self.request.GET['event_id'])
        else:
            messages.error(self.request, "Url Error")
            return self.form_invalid(form)

        # Host User review participant (True)
        if 'to_user_id' in self.request.GET:
            to_user = User.objects.get(pk=self.request.GET['to_user_id'])
            form.instance.event_host = True
        else:
            to_user = User.objects.get(pk=joined_event.host_user.id) # pkを取得 評価対象


        ## Validators

        # params
        from_reviews = self.request.user.from_rate_user.all()
        to_from_event_list = []
        for review in from_reviews:
            to_from_event_list.append([review.to_rate_user,
                                       review.from_rate_user,
                                       review.joined_event])

        # Past joined_or_hosted_event or not
        if (joined_event not in self.request.user.get_past_participated_events()) and (joined_event not in self.request.user.get_past_hosted_events()):
            messages.error(self.request, "Invalid Review")
            return self.form_invalid(form)

        # from_User is Host or Participant
        if (self.request.user not in joined_event.participant.all()) and (self.request.user != joined_event.host_user):
            # form.add_error('rating', 'Incident with this email already exist')
            messages.error(self.request, "Invalid Review")
            return self.form_invalid(form)

        # to_User is Host or Participant
        if (to_user not in joined_event.participant.all()) and (to_user != joined_event.host_user):
            # form.add_error('rating', 'Incident with this email already exist')
            messages.error(self.request, "Invalid Review")
            return self.form_invalid(form)

        # from user Participant -> Host or not
        if (self.request.user in joined_event.participant.all()) and (to_user != joined_event.host_user):
            messages.error(self.request, "Invalid Review")
            return self.form_invalid(form)

        # from user Host -> Participant or not
        if (self.request.user == joined_event.host_user) and (to_user not in joined_event.participant.all()):
            messages.error(self.request, "Invalid Review")
            return self.form_invalid(form)

        # Check Already Reviewed or not
        if [to_user, self.request.user, joined_event] in to_from_event_list:
                messages.error(self.request, "You Already Reviewd")
                return self.form_invalid(form)




        # Set Instanse
        form.instance.to_rate_user_id = to_user.id
        form.instance.from_rate_user_id = self.request.user.id # 評価者 <--
        form.instance.joined_event_id = joined_event.id
        form.save()
        return super(UserPostReviewView, self).form_valid(form)

    # レビュー投稿時に未レビューページに帰還
    def get_success_url(self, **kwargs):

        messages.info(self.request, "Your review was successfully sent")
        return reverse('user:unreviewed')


class UserUnReviewedView(ListView):
    # なぜ model and form_class がセットでも動くのかわかりません。
        model = User
        template_name = 'user/user_unreviewed.html'

class UserSkillView(DetailView):
    model = User
    template_name = "user/user_skill.html"


class UserSkillEditView(UpdateView):
    model = Skill
    tamplate_name = 'user/user_form.html'
    fields = ['skilltodo']


    def form_valid(self,form):
        form_redirect = super(UserSkillEditView, self).form_valid(form)
        skill = form.save(commit=False)

        new_tags = set([int(t) for t in self.request.POST.getlist('tags')])
        old_tags = set([t.id for t in skill.tag.all()])

        for tag_id in new_tags - old_tags:
            skill.tag.add(tag_id)

        for tag_id in old_tags - new_tags:
            skill.tag.remove(tag_id)

        return form_redirect

    def get_context_data(self, **kwargs):
        context = super(UserSkillEditView, self).get_context_data(**kwargs)
        context['all_tags'] = Tag.objects.all
        return context

    def get_success_url(self, **kwargs):
        messages.info(self.request, "スキル内容を変更しました")
        userskill_id = self.request.user.id
        return reverse('user:skill', kwargs={'pk': userskill_id})

@method_decorator(login_required, name='dispatch')
class UserSkillAddView(CreateView):
    model = Skill
    fields = ['skilltodo']
    success_url = "../../"
    template_name = "user/skill_add.html"
    def get_context_data(self, **kwargs):
        context = super(UserSkillAddView, self).get_context_data(**kwargs)
        context['all_tags'] = Tag.objects.all
        return context

    def form_valid(self, form):
        form_redirect = super(UserSkillAddView, self).form_valid(form)
        skill = form.save()
        skill.tag.clear()
        for tag_id in self.request.POST.getlist('tags'):
            skill.tag.add(int(tag_id))

        form.instance.userskill_id = self.request.user.id
        form.save()
        return form_redirect

    def get_success_url(self, **kwargs):
        messages.info(self.request, _("Your new skill has been added successfully."))
        userskill_id = self.request.user.id
        return reverse('user:skill', kwargs={'pk': userskill_id})
