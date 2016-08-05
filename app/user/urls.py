from django.conf.urls import url, include
from . import views

app_name = 'user'

urlpatterns = [
    url(r'^(?P<user_id>[0-9]+)/$', views.IndexView.view, name='userpage'),
    #url(r'^$', views.IndexView.view,name='userpage'),
]
