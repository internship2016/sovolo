
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': "user/login_page.html"}, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^registor/$', views.ParticipatorCreateView.as_view(), name='registor'),
    url(r'^(?P<pk>[0-9]+)/$', views.ParticipatorDetailView.as_view(), name='detail'),
]

