from django.conf.urls import url, include
from . import views

app_name = 'group'

urlpatterns = [
    # group/
    url(r'^$',
        views.GroupIndexView.as_view(), name='index'),

    # group/1/detail
    url(r'^(?P<pk>[0-9]+)/$',
        views.GroupDetailView.as_view(), name='detail'),

    # group/1/delete
    url(r'^(?P<pk>[0-9]+)/delete/$',
        views.GroupDeleteView.as_view(), name='delete'),

    # group/1/edit/
    url(r'^(?P<pk>[0-9]+)/edit/$',
        views.GroupEditView.as_view(), name='edit'),

    # group/add
    url(r'^add/$',
        views.GroupCreate.as_view(), name='add'),
]
