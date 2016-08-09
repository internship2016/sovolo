from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from .models import Event

from django.utils import timezone

# Create your views here.


def detail(request, event_id):
    return render(request, 'event/detail.html', {'event_id':event_id})

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

def add(request):
    return render(request, 'event/add.html')

class EventCreate(CreateView):
    model = Event
    fields = ['name', 'start_time', 'end_time', 'meeting_place', 'place', 'image', 'contact', 'details', 'notes', 'ticket', 'region']

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
