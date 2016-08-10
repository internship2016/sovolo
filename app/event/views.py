from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from django.core.urlresolvers import reverse_lazy
from .models import Event, Participation

from django.utils import timezone

# Create your views here.


def manage(request,event_id):
    data ={
        'event_id':event_id
    }
    return render(request, 'event/manage.html', data)


def participants(request,event_id):
    data ={
        'event_id':event_id
    }
    return render(request, 'event/participants.html', data)


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