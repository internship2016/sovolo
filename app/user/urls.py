from django.conf.urls import url, include
from . import views
from django.contrib.auth import views as auth_views

app_name = 'user'

urlpatterns = [
    url(r'^(?P<user_id>[0-9]+)/$', views.IndexView.view, name='user_page'),
    url(r'^login/$', auth_views.login, {'template_name': "user/login_page.html"}, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    # url(r'^register/$', auth_views.registration, name='register'),
]
