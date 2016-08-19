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
        form_redirect = super(GroupCreate, self).form_valid(form)
        group = form.save(commit=False)

        # Events
        new_events = set([int(e) for e in self.request.POST.getlist('events')])
        old_events = set([e.id for e in self.request.user.admin_event.all()])

        for event_id in set(new_events) - set(old_events):
            group.event.add(event_id)

        for event_id in set(old_events) - set(new_events):
            group.event.remove(event_id)

        # Admins
        raw_admins = self.request.POST.getlist('admins')
        new_admins, new_admin_names = zip(*User.objects.filter(username__in=raw_admins).values_list('id','username'))
        old_admins = group.admins().values_list('id', flat=True)

        for admin in set(new_admins) - set(old_admins) | {self.request.user.id}:
            membership = group.membership_set.get_or_create(member_id=admin)[0]
            membership.role = 'admin'
            membership.save()

        for admin in set(old_admins) - set(new_admins):
            group.membership_set.get(member_id=admin).role = 'Normal'

        for name in set(raw_admins) - set(new_admin_names):
            messages.error(self.request, "ユーザ名 " + name + " に一致するユーザーはいませんでした。")

        messages.info(self.request, "グループを作成しました。")
        return form_redirect


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
        form_redirect = super(GroupEditView, self).form_valid(form)
        group = form.save(commit=False)

        # Events
        new_events = set([int(e) for e in self.request.POST.getlist('events')])
        old_events = set(group.event.filter(admin__in=[self.request.user]).values_list('id', flat=True))

        messages.info(self.request, new_events)
        messages.info(self.request, old_events)

        for event_id in set(new_events) - set(old_events):
            group.event.add(event_id)

        for event_id in set(old_events) - set(new_events):
            group.event.remove(event_id)

        # Admins
        raw_admins = self.request.POST.getlist('admins')
        try:
            new_admins, new_admin_names = zip(*User.objects.filter(username__in=raw_admins).values_list('id', 'username'))
            old_admins = group.admins().values_list('id', flat=True)

            for admin in set(new_admins) - set(old_admins):
                membership = group.membership_set.get_or_create(member_id=admin)[0]
                membership.role = 'admin'
                membership.save()

            for admin in set(old_admins) - set(new_admins):
                group.membership_set.get(member_id=admin).role = 'Normal'

            for name in set(raw_admins) - set(new_admin_names):
                messages.error(self.request, "ユーザ名 " + name + " に一致するユーザーはいませんでした。")

            messages.info(self.request, "グループを作成しました。")
        except ValueError:
            messages.error(self.request, "管理者の変更に失敗しました。")
            pass

        return form_redirect

    def test_func(self):
        return self.request.user in self.get_object().admins()

    def handle_no_permission(self):
        return HttpResponseForbidden()


class GroupDeleteView(DeleteView):
    template_name = 'group/check_delete.html'
    model = Group
    success_url = reverse_lazy('group:index')
