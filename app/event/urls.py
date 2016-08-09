#coding=utf-8
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name='event'

urlpatterns = [
    url(r'^$', views.EventIndexView.as_view(), name='index'),
    url(r'^(?P<pk>[0-9]+)/$', views.EventDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.EventDeleteView.as_view(), name='delete'),
    url(r'^(?P<event_id>[0-9]+)/manage/$', views.manage, name='manage'),
    url(r'^(?P<pk>[0-9]+)/edit/$', views.EventEditView.as_view(), name='edit'),
    url(r'^(?P<event_id>[0-9]+)/participants/$', views.participants, name='participants'),
    #url(r'^add/$', views.add, name='add'),
    #Event追加
    url(r'^add/$', views.EventCreate.as_view(), name='event-add'),
]