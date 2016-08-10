from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from django.core.urlresolvers import reverse_lazy
from .models import User

from django.utils import timezone

# Create your views here.

class IndexView:
    def view(request,user_id):
        data = {
            "user_id":user_id
            }
        return render(request,"user/user_page.html",data)


def login_view(request):
    return render(request, "user/login_page.html")


def register_view(request):
    return render(request, "user/register_page.html")



class UserDetailView(DetailView):
    template_name = 'user/detail.html'
    model = User
    context_object_name = 'user'
    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

class UserEditView(UpdateView):
    model = User
    fields = ['nickname']
    template_name = 'user/edit.html'

class UserDeleteView(DeleteView):
    model = User
    success_url = reverse_lazy('event:index')
    template_name = 'user/check_delete.html'
