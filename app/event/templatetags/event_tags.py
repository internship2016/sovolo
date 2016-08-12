from django import template

register = template.Library()


@register.inclusion_tag('event/event_list.html')
def event_list(events):
    return {'events': events}