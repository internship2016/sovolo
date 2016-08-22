from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView, View
from django.contrib  import messages
from django.core.urlresolvers import reverse_lazy
from .models import User
from tag.models import Tag
from django.contrib.auth import views as auth_views

from django.utils import timezone
from .models import User


class UserCreateView(CreateView):
    model = User
    fields = ['email', 'password', 'username']
    template_name = 'user/register.html'

    def form_valid(self, form):
        from django.contrib.auth import login
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        login(self.request, user, "django.contrib.auth.backends.ModelBackend")
        messages.info(self.request, "ユーザー登録が完了しました。")
        return super(UserCreateView, self).form_valid(form)

    def get_form(self):
        from django import forms
        form = super().get_form()
        form.fields['password'].widget = forms.PasswordInput()
        return form


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

        messages.info(self.request, "ユーザ情報を編集しました。")
        return super(UserEditView, self).form_valid(form)

    def form_invalid(self, form):
        for field, msg in form.errors.items():
            messages.error(self.request, field + ': ' + '/'.join(msg))
        return super().form_invalid(form)


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
