from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseForbidden
from event.models import Event
from user.models import User
from .models import Group
# Create your views here.


class GroupCreate(CreateView):
    template_name = 'group/add.html'
    model = Group
    fields = ['name','description','image']

    def form_valid(self, form):
        return super(GroupCreate, self).form_valid(form)


class GroupDetailView(DetailView):
    template_name = 'group/detail.html'
    model = Group
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        context = super(GroupDetailView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


class GroupMembersView(DetailView):
    template_name = 'group/members.html'
    model = Group
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        context = super(GroupMembersView, self).get_context_data(**kwargs)
        context['admins']  = [ m.member for m in self.object.membership_set.all() if m.role == 'admin']
        context['members'] = [ m.member for m in self.object.membership_set.all() if m.role == 'Normal']
        return context


class GroupIndexView(ListView):
    template_name = 'group/index.html'
    context_object_name = 'all_groups'

    def get_queryset(self):
        return Group.objects.all()


class GroupEditView(UserPassesTestMixin, UpdateView):
    template_name = 'group/edit.html'
    model = Group
    fields = ['name', 'image', 'description']

    def form_valid(self, form):
        self.object = form.save(commit=False)

        names = self.request.POST.getlist('admins')
        for name in names:
            try:
                user = User.objects.get(username=name)
                self.object.membership_set.get_or_create(member=user, role='admin')
            except ObjectDoesNotExist:
                messages.error(self.request, "ユーザ名 "+name+" に一致するユーザーはいませんでした。")

        event_ids = self.request.POST.getlist('events')
        events = list(map(lambda pk: Event.objects.get(pk=pk), event_ids))
        self.object.event.add(*events)

        messages.info(self.request, "変種しました。")
        return super(GroupEditView, self).form_valid(form)

    def test_func(self):
        return self.request.user in self.get_object().admins()

    def handle_no_permission(self):
        return HttpResponseForbidden()


class GroupDeleteView(DeleteView):
    template_name = 'group/check_delete.html'
    model = Group
    success_url = reverse_lazy('group:index')
