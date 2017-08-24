from django.http import JsonResponse
from event.models import Event
from django.apps import apps
from django.db.models import Q
from tag.models import Tag

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def event_filter(request, event_kind, *args, **kwargs):
    """Event Filter.
    リクエストのあったイベントを新規イベントは作成日時順、
    他は開始日時順の若い方から10件をjsonで返す。
    """
    if request.method != 'POST':
        return JsonResponse(dict())

    def all_events():
        return Event.objects.all().order_by('-created')[:10]

    def new_events():
        return [event for event in all_events() if not event.is_over()]

    user = request.user
    events = {'new_events': new_events}
    if not user.is_anonymous():
        events.update({
            'future_participating_events': user.get_future_participating_events,
            'new_region_events': user.get_new_region_events,
            'new_tag_events': user.get_new_tag_events,
            'all_events': all_events
        })
    if event_kind in events.keys():
        res_obj = {'filtered_events': []}
        for event in events[event_kind]()[:10]:
            res_obj['filtered_events'].append({
                'id': event.id,
                'name': event.name,
                'start_time': event.start_time.strftime(DATETIME_FORMAT),
                'end_time': event.end_time.strftime(DATETIME_FORMAT),
                'place': event.meeting_place,
                'img': event.get_image_url(),
                'status': event.get_status()
            })
        return JsonResponse(res_obj)

def event_range_search(request, *args, **kwargs):
    if request.method != 'POST':
        # FIXME: 405 Method Not Allowed
        return None
    query = Q()
    res = {'events_in_range': []}
    range_value = dict(request.POST)
    keys = ['ne_lat', 'sw_lat', 'ne_lng', 'sw_lng']
    for key in keys:
        range_value[key] = float(range_value[key][0])

    events = Event.get_events_in_range(range_value['ne_lat'],
                                       range_value['sw_lat'],
                                       range_value['ne_lng'],
                                       range_value['sw_lng'])



    tags = [int(t) for t in request.POST.getlist('tags')]
    if len(tags) > 0:
        Tag = apps.get_model('tag', 'Tag')
        tag_query = None
        for t in tags:
            tag = Tag.objects.get(pk=t)
            if tag_query is None:
                tag_query = Q(tag=tag)
            else:
                tag_query = tag_query | Q(tag=tag)
        query = query & tag_query
    events = [event for event in events.all().filter(query).order_by('-id').distinct() if not event.is_over()]

    for event in events:
        res['events_in_range'].append({
            'id': event.id,
            'name': event.name,
            'start_time': event.start_time.strftime(DATETIME_FORMAT),
            'end_time': event.end_time.strftime(DATETIME_FORMAT),
            'place': event.meeting_place,
            'longitude': event.longitude,
            'latitude': event.latitude,
            'img': event.get_image_url(),
            'status': event.get_status()
        })

    return JsonResponse(res)
