from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import Http404
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseForbidden
from event.models import Event
from user.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Group, Membership
# Create your views here.


@method_decorator(login_required, name='dispatch')
class GroupCreate(CreateView):
    template_name = 'group/add.html'
    model = Group
    fields = ['name','description','image']

    def form_valid(self, form):
        redirect = super(GroupCreate, self).form_valid(form)
        group = form.save(commit=False)

        group.membership_set.get_or_create(member=self.request.user, role='admin')
        names = self.request.POST.getlist('admins')
        for name in names:
            try:
                user = User.objects.get(username=name)
                group.membership_set.get_or_create(member=user, role='admin')
            except ObjectDoesNotExist:
                messages.error(self.request, "ユーザ名 "+name+" に一致するユーザーはいませんでした。")

        event_ids = self.request.POST.getlist('events')
        events = list(map(lambda pk: Event.objects.get(pk=pk), event_ids))
        group.event.add(*events)

        messages.info(self.request, "グループを作成しました。")
        return redirect


class GroupDetailView(DetailView):
    template_name = 'group/detail.html'
    model = Group
    context_object_name = 'group'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            messages.error(request, "そのグループは存在しません")
            return redirect('top')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

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
        group = form.save(commit=False)

        old_admins = set([u.username for u in group.admins()])
        new_admins = set(self.request.POST.getlist('admins'))

        Membership.objects.filter(group=group, member__username__in=list(old_admins - new_admins), role='admin').delete()

        for name in new_admins - old_admins:
            try:
                user = User.objects.get(username=name)
                group.membership_set.get_or_create(member=user, role='admin')
            except ObjectDoesNotExist:
                messages.error(self.request, "ユーザ名 "+name+" に一致するユーザーはいませんでした。")

        event_ids = self.request.POST.getlist('events')
        events = list(map(lambda pk: Event.objects.get(pk=pk), event_ids))
        if len(events) is not 0:
            group.event.add(*events)

        messages.info(self.request, "グループを編集しました。")
        return super(GroupEditView, self).form_valid(form)

    def test_func(self):
        return self.request.user in self.get_object().admins()

    def handle_no_permission(self):
        return HttpResponseForbidden()


class GroupDeleteView(DeleteView):
    template_name = 'group/check_delete.html'
    model = Group
    success_url = reverse_lazy('group:index')
