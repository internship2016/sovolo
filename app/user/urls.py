from django.conf.urls import url, include
from . import views
from django.contrib.auth import views as auth_views

app_name = 'user'

urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': "user/login_page.html"}, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    # url(r'^register/$', auth_views.registration, name='register'),

    # user/1/detail
    url(r'^(?P<pk>[0-9]+)/$', views.UserDetailView.as_view(), name='detail'),
    # user/1/edit/
    url(r'^(?P<pk>[0-9]+)/edit/$', views.UserEditView.as_view(), name='edit'),
    # user/1/delete
    url(r'^(?P<pk>[0-9]+)/delete/$', views.UserDeleteView.as_view(), name='delete'),
]
