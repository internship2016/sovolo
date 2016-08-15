from django.conf.urls import url, include
from . import views
from django.contrib.auth import views as auth_views

app_name = 'user'


urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': "user/login_page.html"}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': "user/logout.html", 'redirect_field_name':'top'},  name='logout'),
    url(r'^register/$', views.UserCreateView.as_view(), name='register'),
    url(r'^email_required/$', views.AcquireEmail.as_view(), name='acquire_email'),
    url(r'^edit/$', views.UserEditView.as_view(), name='edit'),

    # user/1/detail
    url(r'^(?P<pk>[0-9]+)/$', views.UserDetailView.as_view(), name='detail'),
]
