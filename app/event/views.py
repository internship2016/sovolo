from django.shortcuts import render

# Create your views here.


def detail(request, event_id):
    return render(request, 'event/detail.html', event_id)