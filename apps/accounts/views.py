from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.forms import ProfileForm
from apps.accounts.models import Profile
from apps.main.models import Goal
from apps.main.services.helpers import calculate_calories
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse

# Create your views here.

def set_jwt_cookies(response, user):
    refresh = RefreshToken.for_user(user)
    response.set_cookies(
        key='access_token',
        values=str(refresh.access_token),
        httponly=True,
        secure=False,   #True in Production
        samesite='Lax'
    )
    response.set_cookie(
        key='refresh_token',
        value=str(refresh),
        httponly=True,
        secure=False,
        samesite='Lax',
    )
    return response


def signup_view(request):
    goals = Goal.objects.all()
    
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        goal_id = request.POST.get("goal")
                
    
        
        if password != confirm_password:
            print("PASSWORD MISMATCH")
            return render(request, 'signup.html', {
                "error": "Passwords do not match",
                "goals":goals
            })
        
        if User.objects.filter(username=username).exists():
            return render(
                request, 'signup.html',{
                    "error":"User is already exists !!",
                    "goals":goals
            })
        if User.objects.filter(email=email).exists():
            return render(
                request,"signup.html", {
                    "error":"Email already exists use new email !!",
                    "goals":goals}
            )          
        
        try:
            selected_goal = Goal.objects.get(pk=goal_id)
        except (Goal.DoesNotExist, ValueError):
            return render(request, 'signup.html', {
                "error": "Please select a valid goal",
                "goals": goals
            })
        
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        Profile.objects.create(
            user=user,
            goal=selected_goal
        )
        response = redirect("main:home")
        response = set_jwt_cookies(response,user)
        messages.success(request, f"Welcome, {username}! Your account has been created.")
        return response
        
    return render(request, 'signup.html', {'goals': goals})


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
            # --- JWT cookies on login ---
            response = redirect("dashboard:dashboard")
            response = set_jwt_cookies(response, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return response
        else:
            messages.error(request, "Invalid email/username or password.")
            return render(request, 'login.html')
            
    return render(request, 'login.html')
 
def logout_view(request):
    response = redirect('accounts:login')
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    logout(request)
    messages.info(request, "You have been logged out.")
    return response

@login_required
def profile_view(request):
    """
    Read‑only profile page (optional – can be used if you want a standalone page).
    """
    profile = request.user.profile
    calorie_data = None
    if (profile.age and profile.gender and profile.height_cm and
        profile.current_weight_kg and profile.activity_level and profile.goal):
        calorie_data = calculate_calories(
            age=profile.age,
            gender=profile.gender,
            height=profile.height_cm,
            weight=profile.current_weight_kg,
            activity=profile.activity_level,
            goal=profile.goal
        )
    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'calorie_data': calorie_data,
    })


@login_required
def update_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        # Update fields manually from the custom form
        profile.goal_id = request.POST.get('goal') or profile.goal_id
        profile.level_id = request.POST.get('level') or profile.level_id
        profile.yoga_level_id = request.POST.get('yoga_level') or profile.yoga_level_id
        profile.home_gym_preference = request.POST.get('home_gym_preference') or profile.home_gym_preference
        profile.diet_preference = request.POST.get('diet_preference') or profile.diet_preference
        profile.age = request.POST.get('age') or None
        profile.gender = request.POST.get('gender') or None
        profile.height_cm = request.POST.get('height_cm') or None
        profile.current_weight_kg = request.POST.get('current_weight_kg') or None
        profile.activity_level = request.POST.get('activity_level') or None
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        profile.save()

        messages.success(request, "Profile updated successfully!")

        # Redirect back to dashboard with hash for settings tab
        redirect_hash = request.POST.get('redirect_hash', '')
        url = reverse('dashboard:dashboard')
        if redirect_hash:
            url += f'#{redirect_hash}'
        return redirect(url)

    # GET request – not used since we never leave the dashboard
    return redirect('dashboard:dashboard')