from django.conf.urls import url, include
from . import views

app_name = 'group'

urlpatterns = [
    url(r'^(?P<group_id>[0-9]+)/$', views.IndexView.view, name='grouppage'),
    
]
