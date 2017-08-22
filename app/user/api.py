from django.http import JsonResponse
from user.models import UserReviewList


def event_filter(request, event_kind, *args, **kwargs):
    """Event Filter.
    リクエストのあったイベントを新規イベントは作成日時順、
    他は開始日時順の若い方から10件をjsonで返す。
    """
    if request.method != 'POST':
        return JsonResponse(dict())
    def new_events():
        return Event.objects.all().order_by('-created')[:10]
    user = request.user
    events = {'new_events' : new_events}
    if not user.is_anonymous():
        events.update({
                'future_participating_events' : user.get_future_participating_events,
                'new_group_events' : user.get_new_group_events,
                'new_region_events' : user.get_new_region_events,
                'new_tag_events' : user.get_new_tag_events
                })
    if event_kind in events.keys():
        res_obj = {'filtered_events':[]}
        for event in events[event_kind]()[:10]:
            res_obj['filtered_events'].append({
                'id' : event.id,
                'name' : event.name,
                'start_time' : event.start_time.strftime(DATETIME_FORMAT),
                'end_time' : event.end_time.strftime(DATETIME_FORMAT),
                'place' : event.meeting_place,
                'img' : event.get_image_url(),
                'status' : event.get_status()
                })
        return JsonResponse(res_obj)
