from django.shortcuts import render

# Create your views here.

class IndexView:
    def view(request,user_id):
        data = {
            "user_id":user_id
            }
        return render(request,"user/userpage.html",data)
