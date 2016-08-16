from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import DetailView, ListView, RedirectView, View
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

import sys
import re
from datetime import datetime
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class EventCreate(CreateView):
    model = Event
    fields = [
        'name',
        'start_time',
        'end_time',
        'meeting_place',
        'place',
        'image',
        'contact',
        'details',
        'notes',
        'ticket',
        'region',
    ]

    template_name = "event/add.html"

    def form_valid(self, form):
        form.instance.host_user = self.request.user
        return super(EventCreate, self).form_valid(form)


class EventDetailView(DetailView):
    template_name = 'event/detail.html'
    model = Event
    context_object_name = 'event'

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
        return Event.objects.all()


class EventEditView(UserPassesTestMixin, UpdateView):
    model = Event
    fields = [
        'name',
        'start_time',
        'end_time',
        'meeting_place',
        'place',
        'image',
        'details',
        'notes',
    ]
    template_name = 'event/edit.html'

    def test_func(self):
        return self.request.user.is_manager_for(self.get_object())

    def handle_no_permission(self):
        return HttpResponseForbidden()


class EventDeleteView(DeleteView):
    model = Event
    success_url = reverse_lazy('event:index')
    template_name = 'event/check_delete.html'

    def get_context_data(self, **kwargs):
        context = super(EventDeleteView, self).get_context_data()
        return context

    def dispatch(self, request, *args, **kwargs):
        if self.request.user not in self.get_object().admin.all():
            return HttpResponseForbidden()
        return super(DeleteView, self).dispatch(request, *args, **kwargs)


class EventParticipantsView(ListView):
    model = Participation
    template_name = 'event/participants.html'
    context_object_name = 'all_participants'

    def get_context_data(self, **kwargs):
        context = super(EventParticipantsView, self).get_context_data(**kwargs)
        context['event_id'] = self.kwargs['event_id']
        return context

    def get_queryset(self):
        event_id = self.kwargs['event_id']
        requested_event = Event.objects.get(pk=event_id)

        return Participation.objects.filter(event=requested_event)


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
                date = datetime.strptime(begin_date_string, "%m/%d/%Y")
                date_query = Q(start_time__gte=date)
                query = query & date_query

        if 'end_date' in self.request.GET:
            end_date_string = self.request.GET['end_date']
            if end_date_string is not None and end_date_string != "":
                date = datetime.strptime(end_date_string, "%m/%d/%Y") + datetime.timedelta(days=1)
                date_query = Q(start_time__lt=date)
                query = query & date_query

        #Tag
        if 'tag' in self.request.GET:
            t = self.request.GET['tag']

            if t is not None and t!="":
                Tag = apps.get_model('tag', 'Tag')
                tag = Tag.objects.get(name=t)
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
                g = Group.objects.get(pk=int(group))
                group_list = [g]
                group_query = Q(group__in=group_list)
                query = query & group_query

        results = Event.objects.filter(query)

        #Include events with no openings?
        if 'exclude_full_events' in self.request.GET and self.request.GET['exclude_full_events'] == "on":
            results = [event for event in results if not event.is_full()]

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
            if num_per_page is not None and num_per_page!="":
                self.paginate_by = int(num_per_page)

        return results


@method_decorator(login_required, name='dispatch')
class EventJoinView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        event_id = kwargs['event_id']
        frame_id = kwargs['frame_id']

        frame = Frame.objects.get(pk=frame_id)
        status = "waiting_list" if frame.is_full() else "participating"

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
                if status == "waiting_list":
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
            messages.error(self.request, "この枠はすでに締め切られています。")
        else:
            try:
                p = Participation.objects.create(
                    user=self.request.user,
                    event_id=kwargs['event_id'],
                    status="following",
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

class ParticipationDeleteView(DeleteView):
    model = Participation

    def get_success_url(self):
        if self.object.status == "participating":
            carry_up = self.object.frame.participation_set.filter(status="waiting_list").first()
            carry_up.status = "participating"
            #Send Email
            template = get_template("email/carry_up.txt")
            context = Context({'user': carry_up.user, 'event': carry_up.event})
            content = template.render(context)
            subject = content.split("\n", 1)[0]
            message = content.split("\n", 1)[1]
            send_mail(subject, message, "reminder@sovolo.earth", [carry_up.user.email])


        return reverse_lazy('event:index')


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
