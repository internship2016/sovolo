from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView, View
from django.core.urlresolvers import reverse_lazy
from .models import User

from django.utils import timezone
from .models import User


class UserCreateView(CreateView):
    model = User
    fields = ['email', 'password', 'username']
    template_name = 'user/register.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.set_password(form.cleaned_data['password'])
        self.object.save()
        return super(UserCreateView, self).form_valid(form)


class UserDetailView(DetailView):
    template_name = 'user/detail.html'
    model = User
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


class UserEditView(UpdateView):
    model = User
    fields = ['username', 'email', 'image', 'region', 'sex', 'birthday']
    template_name = 'user/edit.html'

    def get_object(self, queryset=None):
        return self.request.user


class AcquireEmail(View):
    def get(self, request, *args, **kwargs):
        """
        Request email for the create user flow for logins that don't specify their email address.
        """
        backend = request.session['partial_pipeline']['backend']
        return render(request, 'user/acquire_email.html', {"backend": backend})