from django.conf.urls import url, include
from . import views

app_name = 'user'

urlpatterns = [

    url(r'^login/$', views.login_view,name='login'),
    url(r'^register/$', views.register_view,name='register'),
    # user/1/detail
    url(r'^(?P<pk>[0-9]+)/$', views.UserDetailView.as_view(), name='detail'),
    # user/1/edit/
    url(r'^(?P<pk>[0-9]+)/edit/$', views.UserEditView.as_view(), name='edit'),
    # user/1/delete
    url(r'^(?P<pk>[0-9]+)/delete/$', views.UserDeleteView.as_view(), name='delete'),
]
