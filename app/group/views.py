from django.shortcuts import render

# Create your views here.

class IndexView:
    def view(request,group_id):
        data = {
            "group_id":group_id
            }
        return render(request,"group/grouppage.html",data)
