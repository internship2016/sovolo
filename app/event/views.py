from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from .models import Event, Participation

from django.utils import timezone
import re
# Create your views here.

def manage(request,event_id):
    data ={
        'event_id':event_id
    }
    return render(request, 'event/manage.html', data)

class EventCreate(CreateView):
    model = Event
    fields = ['name', 'start_time', 'end_time', 'meeting_place', 'place', 'image', 'contact', 'details', 'notes', 'ticket', 'region']

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
        return context

class EventIndexView(ListView):
    template_name = 'event/index.html'
    context_object_name = 'all_events'
    def get_queryset(self):
        return Event.objects.all()

class EventEditView(UpdateView):
    model = Event
    fields = ['name', 'start_time','end_time','meeting_place', 'place', 'image', 'details', 'notes']
    template_name = 'event/edit.html'

class EventDeleteView(DeleteView):
    model = Event
    success_url = reverse_lazy('event:index')
    template_name = 'event/check_delete.html'


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

    def split_string_to_terms(self, string):
        findterms = re.compile(r'"([^"]+)"|(\S+)').findall
        normspace = re.compile(r'\s{2,}').sub

        return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(string)]

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
        user_entry = self.request.GET['q']

        query = self.make_query_from_string(user_entry)

        return Event.objects.filter(query)
