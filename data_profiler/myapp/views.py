from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# Create your views here.
from django.http import HttpResponse



def index(request):
    return render(request, "authapp/home.html")

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request, "Usernme already exist! please try some other username")
            return redirect('index')
        
        if pass1 != pass2:
            messages.error(request, "Password didn't match!")

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname

        myuser.save()

        messages.success(request, "Your Account has been successfully created.")
        return redirect('signin')
    return render(request, "authapp/signup.html")

def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "authapp/main.html", {'fname': fname})
        else:
            messages.error(request, "Bad Creadentials!")
            return redirect('index')

    return render(request, "authapp/signin.html")

@login_required
def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!")
    return redirect('index')

def delete(request):
    if request.method == "POST":
        username = request.POST['username']
        User.objects.filter(username=username).delete()
        return render(request, "authapp/index.html")

    return render(request, "authapp/delete.html")


def charts(request):
    return render(request, "authapp/charts.html")

def tables(request):
    return render(request, "authapp/tables.html")

def password(request):
    return render(request, "authapp/password.html")

def main(request):
    return render(request, "authapp/main.html")

def settings(request):
    return render(request, "authapp/settings.html")