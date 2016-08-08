from django.conf.urls import url, include
from . import views

app_name='event'

urlpatterns = [
    url(r'^(?P<event_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<event_id>[0-9]+)/edit/$', views.edit, name='edit'),
    url(r'^add/$', views.add, name='add'),
]