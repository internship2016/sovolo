from django.conf.urls import url
from . import views, api
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

app_name = 'user'


def anonymous_required(redirect_url):
    """
    Decorator for views that allow only unauthenticated users to access view.
    Usage:
    @anonymous_required(redirect_url='company_info')
    def homepage(request):
        return render(request, 'homepage.html')
    """
    def _wrapped(view_func, *args, **kwargs):
        def check_anonymous(request, *args, **kwargs):
            view = view_func(request, *args, **kwargs)
            if (not request.user is None) and request.user.is_authenticated:
                return redirect(redirect_url)
            return view
        return check_anonymous
    return _wrapped

# for use in urlpatterns, redirect to home
anonymous_wrapper = anonymous_required("/")

urlpatterns = [
    url(r'^login/$',
        anonymous_wrapper(auth_views.login), {'template_name': "user/login_page.html"},
        name='login'),

    url(r'^logout/$',
        views.logout,
        name='logout'),

    url(r'^register/$',
        views.UserCreateView.as_view(),
        name='register'),

    url(r'^activation/(?P<key>\w+)/$',
        views.UserActivationView.as_view(),
        name='activation'),

    url(r'^email_required/$',
        views.AcquireEmail.as_view(),
        name='acquire_email'),

    url(r'^request_password_reset/$',
        views.RequestPasswordReset.as_view(),
        name='request_password_reset'),

    url(r'^reset_password/(?P<key>\w+)$',
        views.ResetPassword.as_view(),
        name='reset_password'),

    url(r'^edit/$',
        views.UserEditView.as_view(),
        name='edit'),

    # user/1/detail
    url(r'^(?P<pk>[0-9]+)/$',
        views.UserDetailView.as_view(),
        name='detail'),

    # review
    url(r'^skill/(?P<pk>[0-9]+)/edit/$',
        views.UserSkillEditView.as_view(),
        name='skill_edit'),

    url(r'^(?P<user_id>[0-9]+)/skill/add/$',
        views.UserSkillAddView.as_view(),
        name='skill_add'),

    url(r'^post_review/$',
        views.UserPostReviewView.as_view(),
        name='post_review'),

    url(r'^unreviewed/$',
        views.UserUnReviewedView.as_view(),
        name='unreviewed'),

    url(r'^top/list/$',
        views.UserListView.as_view(),
        name='user_find'),

    url(r'^filter/tag_users$',
        api.user_filter, {'user_kind': 'tag_users'},
        name='tag_users'),
]
