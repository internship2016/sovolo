from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import DetailView, ListView, RedirectView, View
from django import forms
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.db import IntegrityError
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import Event, Participation, Comment, Question, Answer, Frame
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.apps import apps
from django.template.loader import get_template
from django.template import Context
from django.core.mail import send_mail
from tag.models import Tag
from user.models import User

import sys
import re
from datetime import datetime
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


@method_decorator(login_required, name='dispatch')
class EventCreate(CreateView):
    model = Event
    fields = [
        'name',
        'start_time',
        'end_time',
        'meeting_place',
        'image',
        'contact',
        'details',
        'notes',
        'private_notes',
        'ticket',
        'region',
    ]

    template_name = "event/add.html"

    def dispatch(self, request, *args, **kwargs):
        return super(EventCreate, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.host_user = self.request.user
        event = form.save()

        # Admins
        event.admin.clear()
        raw_admins = self.request.POST.getlist('admins') or []
        new_admins = User.objects.filter(username__in=raw_admins)

        for admin_id in new_admins.values_list('id', flat=True):
            event.admin.add(admin_id)
        event.admin.add(event.host_user.id)

        for name in set(raw_admins) - set(new_admins.values_list('username', flat=True)):
            messages.error(self.request, "ユーザ名 " + name + " に一致するユーザーはいませんでした。")

        # Groups
        event.group_set.clear()
        for group_id in self.request.POST.getlist('groups'):
            event.group_set.add(int(group_id))

        # Tags
        event.tag.clear()
        for tag_id in self.request.POST.getlist('tags'):
            event.tag.add(int(tag_id))

        # Frames
        frame_numbers = self.request.POST.getlist('frame_number')

        for number in frame_numbers:
            frame_id = self.request.POST.get('frame_' + number + '_id')
            if frame_id is None:
                frame = Frame(event=event)
            else:
                frame = Frame.objects.get(pk=frame_id)

            frame.description = self.request.POST.get('frame_' + number + '_description')
            frame.upper_limit = self.request.POST.get('frame_' + number + '_upperlimit')
            frame.deadline = self.request.POST.get('frame_' + number + '_deadline')
            frame.save()

        messages.info(self.request, "イベントを登録しました。")

        return super(EventCreate, self).form_valid(form)

    def form_invalid(self, form):
        return super(EventCreate, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(EventCreate, self).get_context_data(**kwargs)
        context['all_tags'] = Tag.objects.all
        return context


    def get_success_url(self):
        self.object.admin.add(self.request.user)
        sys.stderr.write("Added User")
        p = Participation(
            user=self.request.user,
            event=self.object,
            status="管理者",
        )
        p.save()
        self.object.participation_set.add(p)
        sys.stderr.write("Added participation")
        return super(EventCreate, self).get_success_url()


class EventDetailView(DetailView):
    template_name = 'event/detail.html'
    model = Event
    context_object_name = 'event'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            messages.error(request, "そのイベントは存在しません")
            return redirect('top')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        login_user = self.request.user
        context['participants'] = self.object.participant.all()
        login_user_participating = login_user in self.object.participant.all()
        context['login_user_participating'] = login_user_participating

        if login_user_participating:
            context['participation'] \
                = Participation.objects \
                               .filter(event=self.object) \
                               .get(user=login_user)

        return context


class EventIndexView(ListView):
    template_name = 'event/index.html'
    context_object_name = 'all_events'

    def get_queryset(self):
        date = timezone.now()
        return Event.objects.filter(start_time__gte=date).order_by('start_time')


class EventEditView(UserPassesTestMixin, UpdateView):
    model = Event
    fields = [
        'name',
        'start_time',
        'end_time',
        'meeting_place',
        'image',
        'details',
        'notes',
        'private_notes',
    ]
    template_name = 'event/edit.html'

    def form_valid(self, form):
        event = form.save(commit=False)

        # Admins
        event.admin.clear()
        raw_admins = self.request.POST.getlist('admins') or []
        new_admins = User.objects.filter(username__in=raw_admins)

        for admin_id in new_admins.values_list('id', flat=True):
            event.admin.add(admin_id)
        event.admin.add(event.host_user.id)

        for name in set(raw_admins) - set(new_admins.values_list('username', flat=True)):
            messages.error(self.request, "ユーザ名 " + name + " に一致するユーザーはいませんでした。")

        # Groups
        event.group_set.clear()
        for group_id in set([int(g) for g in self.request.POST.getlist('groups')]):
            event.group_set.add(group_id)

        # Tags
        new_tags = set([int(t) for t in self.request.POST.getlist('tags')])
        old_tags = set([t.id for t in event.tag.all()])

        for tag_id in new_tags - old_tags:
            event.tag.add(tag_id)

        for tag_id in old_tags - new_tags:
            event.tag.remove(tag_id)

        # Frames
        frame_numbers = self.request.POST.getlist('frame_number')

        for number in frame_numbers:
            frame_id = self.request.POST.get('frame_' + number + '_id')
            if frame_id is None:
                frame = Frame(event=event)
            else:
                frame = Frame.objects.get(pk=frame_id)

            frame.description = self.request.POST.get('frame_' + number + '_description')
            frame.upper_limit = self.request.POST.get('frame_' + number + '_upperlimit')
            frame.deadline = self.request.POST.get('frame_' + number + '_deadline')
            frame.save()

        messages.info(self.request, "イベント情報を編集しました。")
        return super(EventEditView, self).form_valid(form)

    def test_func(self):
        return self.request.user.is_manager_for(self.get_object())

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(EventEditView, self).get_context_data(**kwargs)
        context['all_tags'] = Tag.objects.all
        return context


class EventDeleteView(UserPassesTestMixin, DeleteView):
    model = Event
    success_url = reverse_lazy('event:index')
    template_name = 'event/check_delete.html'

    def get_context_data(self, **kwargs):
        context = super(EventDeleteView, self).get_context_data()
        return context

    def dispatch(self, request, *args, **kwargs):
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.request.user.is_manager_for(self.get_object())

    def handle_no_permission(self):
        return HttpResponseForbidden()


class EventParticipantsView(DetailView):
    model = Event
    template_name = 'event/participants.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super(EventParticipantsView, self).get_context_data(**kwargs)
        context['participants'] = [ p.user for p in self.object.participation_set.all() ]
        context['admins'] = [ user for user in self.object.admin.all() ]
        return context


class EventSearchResultsView(ListView):
    model = Event
    template_name = 'event/search_results.html'
    context_object_name = 'result_events'
    paginate_by = 10

    def split_string_to_terms(self, string):
        findterms = re.compile(r'"([^"]+)"|(\S+)').findall
        normspace = re.compile(r'\s{2,}').sub

        return [normspace(' ', (t[0] or t[1]).strip()) for t
                in findterms(string)]

    def make_query_from_string(self, string):
        query = None
        fields = ['name', 'details']
        terms = self.split_string_to_terms(string)
        for term in terms:
            term_query = None
            for field in fields:
                q = Q(**{"%s__icontains" % field: term})
                if term_query is None:
                    term_query = q
                else:
                    term_query = term_query | q
            if query is None:
                query = term_query
            else:
                query = query & term_query

        return query

    def get_queryset(self):

        query = Q()

        #TODO: handle DoesNotExist queries for tag and group

        #Free Word
        if 'q' in self.request.GET:
            user_entry = self.request.GET['q']
            if user_entry is not None and user_entry != "":
                freeword_query = self.make_query_from_string(user_entry)
                query = query & freeword_query

        #Date
        if 'date' in self.request.GET:
            begin_date_string = self.request.GET['date']
            if begin_date_string is not None and begin_date_string != "":
                date = datetime.strptime(begin_date_string, "%Y-%m-%d")
                date_query = Q(start_time__gte=date)
                query = query & date_query

        if 'end_date' in self.request.GET:
            end_date_string = self.request.GET['end_date']
            if end_date_string is not None and end_date_string != "":
                date = datetime.strptime(end_date_string, "%Y-%m-%d") + datetime.timedelta(days=1)
                date_query = Q(start_time__lt=date)
                query = query & date_query

        #Tag
        if 'tag' in self.request.GET:
            t = self.request.GET['tag']

            if t is not None and t!="":
                Tag = apps.get_model('tag', 'Tag')
                try:
                    tag = Tag.objects.get(name=t)
                except ObjectDoesNotExist:
                    messages.error(self.request, "検索結果に一致するイベントが見つかりませんでした")
                    return Event.objects.none()
                tag_query = Q(tag=tag)
                query = query & tag_query

        #Place
        if 'area' in self.request.GET:
            place = self.request.GET['area']

            if place is not None and place!="":
                place_query = Q(place=place)
                query = query & place_query

        #Group
        if 'group' in self.request.GET:
            group = self.request.GET['group']

            if group is not None and group!="":
                Group = apps.get_model('group', 'Group')
                try:
                    g = Group.objects.get(pk=int(group))
                except ObjectDoesNotExist:
                    messages.error(self.request, "検索結果に一致するイベントが見つかりませんでした")
                    return Event.objects.none()
                group_list = [g]
                group_query = Q(group__in=group_list)
                query = query & group_query

        results = Event.objects.filter(query)

        #Include events with no openings?
        if 'exclude_full_events' in self.request.GET and self.request.GET['exclude_full_events'] == "on":
            results = [event for event in results if not event.is_full()]

        #Include events that are already over?
        if 'exclude_closed_events' in self.request.GET and self.request.GET['exclude_closed_events'] == "on":
            results = [event for event in results if not event.is_closed()]

        if len(results)==0:
            messages.error(self.request, "検索結果に一致するイベントが見つかりませんでした")

        if 'order_by' in self.request.GET:
            order_by = self.request.GET['order_by']
            if 'desc' in self.request.GET and self.request.GET['desc'] == "on":
                order_by = "-" + order_by
                results = results.order_by(order_by)
            else:
                results = results.order_by(order_by)

        #Filter based on page and number per page
        if 'numperpage' in self.request.GET:
            num_per_page = self.request.GET["numperpage"]
            print(num_per_page, file=sys.stderr)
            if num_per_page is not None and num_per_page!="":
                self.paginate_by = int(num_per_page)

        return results


@method_decorator(login_required, name='dispatch')
class EventJoinView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        event_id = kwargs['event_id']
        frame_id = kwargs['frame_id']

        frame = Frame.objects.get(pk=frame_id)
        status = "キャンセル待ち" if frame.is_full() else "参加中"

        if frame.is_closed():
            messages.error(self.request, "この枠はすでに締め切られています。")
        else:
            try:
                p = Participation.objects.create(
                    user=self.request.user,
                    event_id=kwargs['event_id'],
                    frame_id=kwargs['frame_id'],
                    status=status,
                )
                p.save()
                if status == "キャンセル待ち":
                    messages.error(self.request, "あなたはキャンセル待ちです")
                else:
                    messages.error(self.request, "参加しました。")
            except IntegrityError:
                event = Event.objects.get(pk=event_id)
                if event in self.request.user.participating_event.all():
                    messages.error(self.request, "参加済みです。")
                else:
                    messages.error(self.request, "参加処理中にエラーが発生しました。")

        self.url = reverse_lazy('event:detail', kwargs={'pk': event_id})
        return super(EventJoinView, self).get_redirect_url(*args, **kwargs)


@method_decorator(login_required, name='dispatch')
class EventFollowView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        event_id = kwargs['event_id']
        event = Event.objects.get(pk=event_id)

        if event.is_closed():
            messages.error(self.request, "このイベントはすでに締め切られています。")
        else:
            try:
                p = Participation.objects.create(
                    user=self.request.user,
                    event_id=kwargs['event_id'],
                    status="興味あり",
                )
                p.save()
                messages.error(self.request, "興味ありイベントに追加しました")
            except IntegrityError:
                event = Event.objects.get(pk=event_id)
                if event in self.request.user.participating_event.all():
                    messages.error(self.request, "参加済みです。")
                else:
                    messages.error(self.request, "参加処理中にエラーが発生しました。")

        self.url = reverse_lazy('event:detail', kwargs={'pk': event_id})
        return super(EventFollowView, self).get_redirect_url(*args, **kwargs)


class ParticipationDeleteView(DeleteView, UserPassesTestMixin):
    model = Participation

    def get_object(self, event_id=None, queryset=None):
        return Participation.objects.get(event_id=self.kwargs['event_id'], user=self.request.user)

    def get_success_url(self):

        if self.object.status == "参加中":
            waiting_list = self.object.frame.participation_set.filter(status="キャンセル待ち").order_by('created')
            if len(waiting_list) > 0:
                carry_up = waiting_list.first()
                carry_up.status = "参加中"
                carry_up.save()
                #Send Email
                template = get_template("email/carry_up.txt")
                context = Context({'user': carry_up.user, 'event': carry_up.event})
                content = template.render(context)
                subject = content.split("\n", 1)[0]
                message = content.split("\n", 1)[1]
                send_mail(subject, message, "reminder@sovolo.earth", [carry_up.user.email])

        messages.info(self.request, "参加をキャンセルしました。")
        return reverse_lazy('event:detail', kwargs={'pk': self.kwargs['event_id']})

    def test_func(self):
        return True
        return self.request.user in Event.objects.get(pk=self.request.event_id).participant.all()

    def handle_no_permission(self):
        return HttpResponseForbidden()


class CommentCreate(CreateView):
    model = Comment
    template_name = 'event/add_comment.html'
    fields = ['text']

    def form_valid(self, form):
        form.instance.user = self.request.user
        event_id = self.kwargs['event_id']
        form.instance.event = Event.objects.get(pk=event_id)
        return super(EventCreate, self).form_valid(form)


class SendMessage(UserPassesTestMixin, SingleObjectMixin, View):
    model = Event

    def get(self, request, *args, **kwargs):
        return render(request, 'event/message.html', {'event': self.get_object()})

    def post(self, request, *args, **kwargs):
        messages.success(self.request, "メッセージの送信が完了しました。")
        # TODO: send mail
        return redirect(reverse_lazy('event:detail', kwargs={'pk':kwargs['pk']}))

    def test_func(self):
        return self.request.user.is_manager_for(self.get_object())

    def handle_no_permission(self):
        return HttpResponseForbidden()
