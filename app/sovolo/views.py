from django.shortcuts import render
from event.models import Event


def index(request):
    if request.user.is_anonymous():
        new_events = Event.objects.all().order_by('-created')[:20]
        context = {'new_events': new_events}

        return render(request, 'top_anonymous.html', context)
    else:
        return render(request, 'top.html')