from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView, View
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse_lazy
from .models import Participator 
from tag.models import Tag
from base.utils import send_template_mail
from django.contrib.auth import views as auth_views
import uuid
from django.contrib.auth import login

from django.utils import timezone
from .models import Participator, ParticipatorActivation, ParticipatorPasswordResetting


class ParticipatorCreateView(CreateView):
    model = Participator
    fields = ['email', 'password', 'participatorname']
    template_name = 'participator/registor.html'

    def form_valid(self, form):
        participator = form.save(commit=False)
        participator.set_password(form.cleaned_date['password'])
        participator.is_active = False
        participator.save()

        activation_key = self.create_activation_key()
        activation = PerticipatorActivation(user=participator, key=activation_key)
        activation.save()

        base_url = "/".join(self.request.build_absolute_uri().split("/")[:3])
        activation_url = "{0}/participator/activation/{1}".format(base_url, activation_key)
        
        send_template_mail(
            "email/activation.txt",
            {"activation_url":activation_url},
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
        form.fields['participatorname'].maxlength = 15
        form.fields['participatorname'].label = "ニックネーム(15文字以内)"
        return form

class ParticipatorDetailView(DetailView):
    template_name = 'participator/detail.html'
    model = Participator
    context_object_name = 'participator'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            message.error(request, "そのユーザーは存在しません")
            return redirect('top')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(ParticipatorDetailView, self).get_cotext_data(**kwargs)
        return context


def logout(request):
    messages.info(request, "ログアウトしました")
    return auth_views.logout(request, next_page="/")



