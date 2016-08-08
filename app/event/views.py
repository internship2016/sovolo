from django.shortcuts import render

# Create your views here.


def detail(request, event_id):
    return render(request, 'event/detail.html', {'event_id':event_id})

def edit(request,event_id):
    data ={
        'event_id':event_id
    }
    return render(request, 'event/edit.html', data)

def add(request):
    return render(request, 'event/add.html')