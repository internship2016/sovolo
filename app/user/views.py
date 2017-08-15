from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView, View
from django.contrib  import messages
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse_lazy
from .models import User
from tag.models import Tag
from base.utils import send_template_mail
from django.contrib.auth import views as auth_views
import uuid
from django.contrib.auth import login

from django.utils import timezone
from .models import User, UserActivation, UserPasswordResetting, UserReviewList

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
        activation_url = "{0}/user/activation/{1}".format(base_url, activation_key)

        send_template_mail(
            "email/activation.txt",
            {"activation_url": activation_url},
            "Sovol Info <info@sovol.earth>",
            [user.email],
        )

        messages.info(self.request, "記入したメールアドレス"+user.email+"に確認メールを送信しました。")
        return redirect("top")

    def create_activation_key(self):
        key = uuid.uuid4().hex
        return key

    def get_form(self):
        from django import forms
        form = super().get_form()
        form.fields['password'].widget = forms.PasswordInput()
        form.fields['username'].maxlength = 15
        form.fields['username'].label = "ニックネーム（15文字以内)"
        return form


class UserActivationView(View):
    def get(self, request, *args, **kwargs):
        activation = get_object_or_404(UserActivation, key=kwargs['key'])
        user = activation.user
        user.is_active = True
        user.save()
        login(request, user, "django.contrib.auth.backends.ModelBackend")
        messages.info(request, "本登録が完了しました。")
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

            base_url = "/".join(self.request.build_absolute_uri().split("/")[:3])
            reset_url = "{0}/user/reset_password/{1}".format(base_url, reset_key)

            send_template_mail(
                "email/reset_password.txt",
                {"reset_url": reset_url},
                "Sovol Info<info@sovol.earth>",
                [user.email]
            )

        messages.info(request, "リクエストを受け付けました。メールアドレスが登録されている場合、アドレスにパスワード再設定のリンクが送信されます。")
        return redirect("top")

    def create_reset_key(self):
        key = uuid.uuid4().hex
        return key


class ResetPassword(View):
    def get(self, request, *args, **kwargs):
        resetting = UserPasswordResetting.objects.filter(key=kwargs['key'])
        if not resetting.exists():
            messages.error(request, "無効なURLです")
            return redirect("top")
        else:
            return render(request, 'user/reset_password.html')

    def post(self, request, *args, **kwargs):
        password = request.POST.get('password')

        resetting = UserPasswordResetting.objects.filter(key=kwargs['key'])
        if resetting .exists():
            resetting = resetting .first()
        else:
            messages.error(request, "パスワードの再設定に失敗しました。")
            return redirect("top")

        user = resetting.user
        user.set_password(password)
        user.save()
        login(request, user, "django.contrib.auth.backends.ModelBackend")

        messages.info(request, "パスワードを再設定しました。")
        return redirect("top")


class UserDetailView(DetailView):
    template_name = 'user/detail.html'
    model = User
    context_object_name = 'user'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            messages.error(request, "そのユーザーは存在しません")
            return redirect('top')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        return context


class UserEditView(UpdateView):
    model = User
    fields = ['username', 'email', 'image', 'region', 'sex', 'birthday']
    template_name = 'user/edit.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(UserEditView, self).get_context_data(**kwargs)
        context['all_tags'] = Tag.objects.all
        return context

    def form_valid(self, form):
        user = form.save(commit=False)

        new_tags = set([int(t) for t in self.request.POST.getlist('tags')])
        old_tags = set([t.id for t in user.follow_tag.all()])

        for tag_id in new_tags - old_tags:
            user.follow_tag.add(tag_id)

        for tag_id in old_tags - new_tags:
            user.follow_tag.remove(tag_id)

        messages.info(self.request, "ユーザー情報を編集しました。")
        return super(UserEditView, self).form_valid(form)


class AcquireEmail(View):
    def get(self, request, *args, **kwargs):
        """
        Request email for the create user flow for logins that don't specify their email address.
        """
        backend = request.session['partial_pipeline']['backend']
        return render(request, 'user/acquire_email.html', {"backend": backend})


def logout(request):
    messages.info(request, "ログアウトしました。")
    return auth_views.logout(request, next_page="/")


## Review
class UserReviewView(DetailView):
    model = User
    template_name = 'user/user_review.html'
