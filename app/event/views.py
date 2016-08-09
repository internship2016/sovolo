from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Event



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
