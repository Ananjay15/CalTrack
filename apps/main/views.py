from django.shortcuts import render
from django.contrib import messages
from apps.accounts.models import Profile
from .services.nutrition.calculate import calculate_calories

# Create your views here.
def home(request):
    return render(request, 'home.html')

def foodlog(request):
    return render(request, 'foodlog.html')

def calculator(request):
    if request.method == 'POST':
        age = int(request.POST.get('age'))
        gender = request.POST.get('gender')
        height = float(request.POST.get('height'))
        weight = float(request.POST.get('weight'))
        activity = float(request.POST.get('activity_level'))
        
        if not request.user.is_authenticated:
            messages.error(request,"Plese Login First.")
            return render(request,"calculator.html")
        
        profile = Profile.objects.filter(user=request.user).first()
        
        if not profile:
            messages.warning(request, "Please complete your profile first.")
            return render(request, "calculator.html")
        
        
        goal = profile.goal
        
        
        
        result = calculate_calories(age, gender, height, weight, activity, goal)
        print("result:",result)
        context = {
            'result':result
            }
        return render(
            request,
            'calculator.html',
            context
        )
    
    return render(request, 'calculator.html')

def workout(request):
    return render(request, 'workout.html')

def yoga(request):
    return render(request, 'yoga.html') 