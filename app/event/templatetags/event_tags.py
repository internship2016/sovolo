from django import template
from django.template import Node, Variable

import sys

register = template.Library()


@register.inclusion_tag('event/event_list.html')
def event_list(events, user):
    return {'events': events, 'user': user}

@register.simple_tag
def query_transform(request, **kwargs):
    updated = request.GET.copy()
    for key, value in kwargs.items():
        updated[key] = value
    return updated.urlencode()