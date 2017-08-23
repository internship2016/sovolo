from django.shortcuts import render
from event.models import Event
from tag.models import Tag
from django.conf import settings
from user.models import User, Skill
from django.views.generic import ListView
from django.db.models import Q


def index(request):
    context = {}

    """All Tags
    全てのタグ
    """
    context['all_tags'] = Tag.objects.all()

    """New Events
    新規イベント
    """
    ev_all = Event.objects.all().order_by('-created')
    if request.user.is_anonymous():
        context['new_events'] = ev_all[:20]
    else:
        context['new_events'] = ev_all[:5]

    """Prefectures
    日本の(!)県名
    """
    # FIXME: i18n, how?
    # XXX: PREFECTURES must be sorted right out of the box
    prefs = settings.PREFECTURES.items()
    prefs = sorted(prefs, key=lambda x: x[1][1])
    prefs = [(k, v[0]) for k, v in prefs]
    context['prefectures'] = prefs

    return render(request, 'top.html', context)


def show_map(request):
    context = {}
    context['all_tags'] = Tag.objects.all()

    return render(request, 'map.html',context)


def index_user(request):
    context = {}

    context['all_tags'] = Tag.objects.all()
    return render(request, 'top_user.html', context)

class UserSearchListView(ListView):
    models = Skill
    template_name = 'user/user_search.html'
    context_object_name ='search_user'
    paginate_by = 10

    def get_queryset(self):
        query = Q()

        if 'tags' in self.request.GET:
            tags = [int(t) for t in self.request.GET.getlist('tags')]

            if len(tags) > 0:
                Tag = apps.get_model('tag', 'Tag')
                tag_query = None
                for t in tags:
                    tag = Tag.objects.get(pk=t)
                    if tag_qeuery is None:
                        tag_query = Q(tag=tag)
                    else:
                        tag_query = tag_query | Q(tag=tag)
                query = tag_query
        results = Skill.objects.filter(query).order_by('-id').distinction()
        return results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["all_tags"] = Tag.obhexts.all()
        tags = self.request.GET.getlist('tags')
        context['checked_tags'] = [int(t) for t in tags]

        return context

