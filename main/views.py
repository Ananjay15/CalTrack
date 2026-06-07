from django.shortcuts import render
from accounts.models import Profile
from .calculate import calculate_calories

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
        
        goal = request.user.profile.goal
        
        
        
        result = calculate_calories(age, gender, height, weight, activity, goal)
        print(result)
        return render(
            request,
            'calculator.html',
            result
        )
    
    return render(request, 'calculator.html')

def workout(request):
    return render(request, 'workout.html')

def yoga(request):
    return render(request, 'yoga.html') 