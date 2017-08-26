from django import template

register = template.Library()


@register.inclusion_tag('event/event_list.html', takes_context=True)
def event_list(context, events, title):
    request = context['request']
    return {'events': events, 'title': title, 'user': request.user}


@register.inclusion_tag('event/collapse_event_list.html', takes_context=True)
def collapse_event_list(context, events, title, event_id):
    request = context['request']
    return {'events': events, 'title': title, 'user': request.user, 'event_id': event_id}


@register.simple_tag
def query_transform(request, **kwargs):
    updated = request.GET.copy()
    for key, value in kwargs.items():
        updated[key] = value
    return updated.urlencode()


@register.inclusion_tag('event/comments.html', takes_context=True)
def comments(context, event):
    comment_list = event.comment_set.order_by('created')
    return {'comment_list': comment_list, 'request': context['request'], 'event': event}
