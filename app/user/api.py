from django.http import JsonResponse
from user.models import User, UserReviewList
from django.apps import apps
from django.db.models import Q

def get_unreview_list(request, unreview_kind, *args, **kwargs):
    """Get Unreview List.
    ログインしているユーザーの未レビューの最新５件を返す。
    """
    back_num = 5
    user = request.user # Login User

    res_obj = {'unreviewd_list': []}

    if user.is_anonymous():
        return JsonResponse(res_obj)

    # href="{% url 'user:post_review' %}?event_id={{event_id}}"
    if user.roll == 'helper':
        unreview_list = user.get_past_participated_and_unreviewed_events() # event
        for event in unreview_list[:back_num]:

            res_obj['unreviewd_list'].append({
                'event_id': event.id,
                'name': event.name,
                'host': event.host_user,
                'img': event.get_image_url(),
                'message' : event.name + 'へのレビューをおねがいします。'
            })

    # href="{% url 'user:post_review' %}?event_id={{event_id}}&to_user_id={{p_user_id}}"
    else:
        counter = 0
        unreview_list = user.get_zipped_unreviewed_hosted() # zip(event, user_list)
        for event, user_list in unreview_list:
            if counter >= back_num:
                break

            for h_user in user_list:
                if counter >= back_num:
                    break
                res_obj['unreviewd_list'].append({
                    'event_id': event.id,
                    'name': event.name,
                    'p_user_name': h_user.username,
                    'p_user_id': h_user.pk,
                    'img': event.get_image_url(),
                    'message' : h_user.username + 'さんへのレビューをおねがいします。'
                })
                counter += 1

    return JsonResponse(res_obj)
