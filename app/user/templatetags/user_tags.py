from django import template

import sys

register = template.Library()


@register.inclusion_tag('user/user_list.html', takes_context=True)
def user_list(context, users, title):
    info = {'users': users, 'title': title}
    if 'event' in context:
        info['object'] = context['event']
    return info

@register.inclusion_tag('user/user_list_large.html', takes_context=True)
def user_list_large(context, users, title):
    return {'users': users, 'title': title}

@register.inclusion_tag('user/template_skilllist.html', takes_context=True)
def skill_list(context, skills, title):
    request = context['request']
    return {'skills':skills, 'title':title, 'user':request.user}

@register.simple_tag
def query_transform(request, **kwargs):
    updated = request.GET.copy()
    for key, value in kwargs.items():
        updated[key] = value
    return updated.urlencode()
