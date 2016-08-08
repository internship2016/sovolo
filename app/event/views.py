from django.shortcuts import render

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