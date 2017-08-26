"""sovolo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static


from . import views

urlpatterns = [
    url(r'^$', views.index, name='top'),
    url(r'^event/top/$', views.index_event, name='top_event'),
    url(r'^user/top/$', views.index_user, name='top_user'),
    url(r'^admin/', admin.site.urls),
    url(r'^event/', include('event.urls')),
    url(r'^tag/', include('tag.urls')),
    url(r'^user/', include('user.urls')),
    url(r'^map/', views.show_map, name='show_map'),
    url('', include('social_django.urls', namespace='social')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
]
urlpatterns += static(settings.STATIC_URL,
                      document_root=settings.STATICFILES_DIRS)

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
