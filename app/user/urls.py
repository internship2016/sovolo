from django.conf.urls import url, include
from . import views

app_name = 'user'

urlpatterns = [
    url(r'^(?P<user_id>[0-9]+)/$', views.IndexView.view, name='user_page'),
    url(r'^login/$', views.login_view,name='login'),
    url(r'^register/$', views.register_view,name='register')
]
