from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Profile

# Create your views here.
def signup_view(request):
    print("METHOD:", request.method)
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        goal = request.POST.get("goal")
                
    
        
        if password != confirm_password:
            print("PASSWORD MISMATCH")
            return render(request, 'signup.html', {"error": "Passwords do not match"})
        
        if User.objects.filter(username=username).exists():
            return render(
                request, 'signup.html',{"error":"User is already exists !!"}
            )
        if User.objects.filter(email=email).exists():
            return render(
                request,
                "signup.html", {"error":"Email already exists use new email !!"}
            )
            
        
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        Profile.objects.create(
            user=user,
            goal=goal
        )
        
        login(request,user)
        return redirect("home")
        
    return render(request, 'signup.html')

def login_view(request):
    
    if request.method == "POST":
        identifier = request.POST.get("identifier")
        password = request.POST.get("password")
    
        try:
            user_obj = User.objects.get(email=identifier)
            username = user_obj.username
        except User.DoesNotExist:
            username=identifier
    

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request,user)
            return redirect("home")
        
        return render(
            request,
            'login.html',
            {"error":"Invalid Email or Password"}
        )
            
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')