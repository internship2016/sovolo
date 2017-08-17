from django.http import JsonResponse
from event.models import Event
import json
#リクエストのあったイベントを新規イベントは作成日時順、他は開始日時順の若い方から10件をjsonで返す。
def event_filter(request, event_kind, *args, **kwargs):
    if request.method == 'POST':
        def new_events():
            return Event.objects.all().order_by('-created')[:10]
        events = {
                'future_participating_events' : request.user.get_future_participating_events,
                'new_group_events' : request.user.get_new_group_events,
                'new_region_events' : request.user.get_new_region_events,
                'new_tag_events' : request.user.get_new_tag_events,
                'new_events' : new_events
                }
        if event_kind in events.keys():
            res_obj = {'filtered_events':[]}
            for event in events[event_kind]()[:10]:
                res_obj['filtered_events'].append({
                    'id' : event.id,
                    'name' : event.name,
                    'start_time' : event.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'end_time' : event.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'place' : event.meeting_place,
                    'img' : event.get_image_url(),
                    'status' : event.get_status()
                    })
            return JsonResponse(res_obj)
    else:
        return JsonResponse(dict())
def event_range_search(request,  *args, **kwargs):
    if request.method == 'POST':
        res = {'events_in_range':[]}
        json_data = json.loads(request.body)
        #json_data = json.loads('{"range_value":{"ne_lat" : 0, "sw_lat" :200, "ne_lng" : 0, "sw_lng" : 200 }}')
        range_value = json_data["range_value"]
        for event in Event.get_events_in_range(range_value['ne_lat'], range_value['sw_lat'], range_value['ne_lng'], range_value['sw_lng']):
            res['events_in_range'].append({
                'id' : event.id,
                'name' : event.name,
                'start_time' : event.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                'end_time' : event.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                'place' : event.meeting_place,
                'longitude' : event.longitude,
                'latitude': event.latitude,
                'img' : event.get_image_url(),
                'status' : event.get_status()
                })
        return JsonResponse(res)
