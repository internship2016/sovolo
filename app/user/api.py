from django.http import JsonResponse


def get_unreview_list(request, unreview_kind, *args, **kwargs):
    """Get Unreview List.
    ログインしているユーザーの未レビューの最新５件を返す。
    """
    back_num = 5
    user = request.user  # Login User

    res_obj = {'unreviewd_list': []}

    if user.is_anonymous():
        return JsonResponse(res_obj)

    if user.roll == 'helper':
        unreview_events = user.get_past_participated_and_unreviewed_events()
        for event in unreview_events[:back_num]:

            res_obj['unreviewd_list'].append({
                'event_id': event.id,
                'event_name': event.name,
                'event_host': event.host_user,
                'event_img': event.get_image_url(),
                'message': event.name + 'へのレビューをおねがいします。'
            })

    else:
        counter = 0

        # XXX: Bad method name: zip(event, user_list)
        unreview_events = user.get_zipped_unreviewed_hosted()

        for event, user_list in unreview_events:
            if counter >= back_num:
                break

            for h_user in user_list:
                if counter >= back_num:
                    break
                res_obj['unreviewd_list'].append({
                    'event_id': event.id,
                    'event_name': event.name,
                    'event_host': event.host_user,
                    'event_img': event.get_image_url(),
                    'helper_name': h_user.username,
                    'helper_id': h_user.pk,
                    'helper_img': h_user.get_image_url(),
                    'message': h_user.username + 'さんへのレビューをおねがいします。'
                })
                counter += 1

    return JsonResponse(res_obj)
