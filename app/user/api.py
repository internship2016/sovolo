from django.http import JsonResponse
from user.models import User
from django.db.models import Q
from django.apps import apps


def user_filter(request, *args, **kwargs):
    # 将来的にはpostで、結果に含めるタグを選択できるようにしたい。
    query = Q()
    user = request.user
    tags = user.follow_tag.all()
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
    # ほんとはソボレージ順に並べたい。けど、現状、ソボレージのfieldはないので、id順。追加したい。
    users = User.objects.all() \
                       .filter(query) \
                       .order_by('-id') \
                       .distinct()
    res = {'filtered_users':[]}
    for u in users:
        res['filtered_users'].append({
            'username':u.username,
            'img_url':u.get_image_url()
        })
    return JsonResponse(res)
