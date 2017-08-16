from django.conf.urls import url, include
from . import views
from django.contrib.auth import views as auth_views

app_name = 'user'


urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': "user/login_page.html"}, name='login'),
    url(r'^logout/$', views.logout,  name='logout'),
    url(r'^register/$', views.UserCreateView.as_view(), name='register'),
    url(r'^activation/(?P<key>\w+)/$', views.UserActivationView.as_view(), name='activation'),
    url(r'^email_required/$', views.AcquireEmail.as_view(), name='acquire_email'),

    url(r'^request_password_reset/$', views.RequestPasswordReset.as_view(), name='request_password_reset'),
    url(r'^reset_password/(?P<key>\w+)$', views.ResetPassword.as_view(), name='reset_password'),

    url(r'^edit/$', views.UserEditView.as_view(), name='edit'),
    # user/1/detail
    url(r'^(?P<pk>[0-9]+)/$', views.UserDetailView.as_view(), name='detail'),

    # url(r'^(?P<pk>[0-9]+)/review/$',views.ReviewView, name='review'),
    # url(r'^review/$',views.ReviewView, name='review'),
    url(r'^(?P<pk>[0-9]+)/review/$', views.UserReviewView.as_view(), name='review'),
]
