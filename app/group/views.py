from django.shortcuts import render
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from django.core.urlresolvers import reverse_lazy
from .models import Group
# Create your views here.

class IndexView:
    def view(request,group_id):
        data = {
            "group_id":group_id
            }
        return render(request,"group/grouppage.html",data)

class GroupCreate(CreateView):
    template_name = 'group/group_form.html'
    model = Group
    fields = ['name', 'image']

    def form_valid(self, form):
        return super(GroupCreate, self).form_valid(form)

class GroupDetailView(DetailView):
    template_name = 'group/detail.html'
    model = Group
    context_object_name = 'group'
    def get_context_data(self, **kwargs):
        context = super(GroupDetailView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

class GroupIndexView(ListView):
    template_name = 'group/index.html'
    context_object_name = 'all_groups'
    def get_queryset(self):
        return Group.objects.all()

class GroupEditView(UpdateView):
    template_name = 'event/edit.html'
    model = Group
    fields = ['name', 'image', 'description']

class GroupDeleteView(DeleteView):
    template_name = 'group/check_delete.html'
    model = Group
    success_url = reverse_lazy('group:index')
