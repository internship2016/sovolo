from django.shortcuts import render

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