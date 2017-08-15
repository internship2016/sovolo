from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

from . import views, api

app_name = 'event'

urlpatterns = [
    # event/
    url(r'^$',
        views.EventIndexView.as_view(), name='index'),

    # event/1/detail
    url(r'^(?P<pk>[0-9]+)/$',
        views.EventDetailView.as_view(), name='detail'),

    # event/1/delete
    url(r'^(?P<pk>[0-9]+)/delete/$',
        views.EventDeleteView.as_view(), name='delete'),

    # event/1/edit/
    url(r'^(?P<pk>[0-9]+)/edit/$',
        views.EventEditView.as_view(), name='edit'),

    # event/<id>/edit/message
    url(r'^(?P<pk>[0-9]+)/edit/message$',
        views.SendMessage.as_view(), name='message'),

    # event/1/participants/
    url(r'^(?P<pk>[0-9]+)/participants/$',
        views.EventParticipantsView.as_view(), name='participants'),

    # event/add
    url(r'^add/$',views.EventCreate.as_view(), name='add'),

    # event/search
    url(r'^search/$',views.EventSearchResultsView.as_view(), name='search'),

    # event/list
    url(r'^list/future_participating_events$', api.event_filter, {'event_kind':'future_participating_events'}, name='list'),
    url(r'^list/new_group_events$', api.event_filter, {'event_kind':'new_group_events'}, name='list'),
    url(r'^list/new_region_events$', api.event_filter, {'event_kind':'new_region_events'}, name='list'),
    url(r'^list/new_tag_events$', api.event_filter, {'event_kind':'new_tag_events'}, name='list'),
    url(r'^list/new_events$', api.event_filter, {'event_kind':'new_events'}, name='list'),

    url(r'^list/(?P<event_kind>[\w_]+)$', api.event_filter, name='list'),


    # event/id/participate/frame_id
    url(r'^(?P<event_id>[0-9]+)/participate/(?P<frame_id>[0-9]+)$', views.EventJoinView.as_view(), name='participate'),

    # event/id/follow
    url(r'(?P<event_id>[0-9]+)/follow$', views.EventFollowView.as_view(), name='follow'),

    # event/id/support
    url(r'(?P<event_id>[0-9]+)/support$', views.EventSupportView.as_view(), name='support'),

    # event/1/cancel
    url(r'^(?P<event_id>[0-9]+)/cancel/$',
        views.ParticipationDeleteView.as_view(), name='cancel'),

    # event/1/comment
    url(r'^(?P<event_id>[0-9]+)/comment/$',
        views.CommentCreate.as_view(), name='comment'),

    # event/comment/1/delete
    url(r'^(?P<event_id>[0-9]+)/comment/(?P<pk>[0-9]+)/delete$',
        views.CommentDeleteView.as_view(), name='comment_delete'),
]
