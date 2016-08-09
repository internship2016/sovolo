#coding=utf-8
from django.conf.urls import url, include
from . import views

app_name='event'

urlpatterns = [
    url(r'^(?P<event_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<event_id>[0-9]+)/manage/$', views.manage, name='manage'),
    url(r'^(?P<event_id>[0-9]+)/participants/$', views.participants, name='participants'),
    url(r'^add/$', views.EventCreate.as_view(), name='add')
]