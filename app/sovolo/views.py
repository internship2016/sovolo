from django.shortcuts import render
from event.models import Event
from tag.models import Tag
from django.conf import settings


def index(request):
    all_tags = Tag.objects.all()
    context = {
        'all_tags': all_tags,
        'prefectures': [(key, value[0]) for key, value in sorted(settings.PREFECTURES.items(), key=lambda x:x[1][1])]
    }

    if request.user.is_anonymous():
        new_events = Event.objects.all().order_by('-created')[:20]
        context['new_events'] = new_events
        return render(request, 'top_anonymous.html', context)
    else:
        return render(request, 'top.html', context)