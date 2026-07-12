from django.shortcuts import render
from django.contrib import messages
from apps.accounts.models import Profile
from apps.main.models import Workout, Yoga, Food
from apps.main.services.helpers import (
    calculate_calories,
    get_goal_from_string,
    split_meal_calories,
    calculate_macros,
)

# Create your views here.
def home(request):
    return render(request, 'home.html')

def diet(request):
    """
    Public diet page – shows 7‑day plans for Weight Loss, Maintenance, Muscle Gain.
    """
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_target = 2000   # sample target – could be different per goal but kept simple

    # Goals to generate plans for
    goal_slugs = ['weight_loss', 'general_fitness', 'muscle_gain']   # 'general_fitness' acts as Maintenance
    all_plans = {}   # key = goal_slug, value = weekly_plan list

    for goal_slug in goal_slugs:
        goal_obj = get_goal_from_string(goal_slug)
        weekly_plan = []
        total_kcal = 0
        total_protein = 0
        total_carbs = 0
        total_fats = 0

        for day_index in range(7):
            meal_budgets = split_meal_calories(daily_target)
            day_data = {'day_index': day_index, 'meals': {}, 'daily_macros': {}}
            daily_macros = {'calories': 0, 'protein_g': 0, 'carbs_g': 0, 'fats_g': 0}

            for meal_type, target_cal in meal_budgets.items():
                foods = Food.objects.filter(
                    goal=goal_obj,
                    meal_type__slug=meal_type
                )
                if not foods.exists():
                    foods = Food.objects.filter(meal_type__slug=meal_type)

                selected = foods.order_by('?')[:2]
                meal_macros = calculate_macros(selected)

                combined = {
                    'name': ' & '.join(f.name for f in selected) if selected else 'No meal',
                    'description': ' | '.join(f.description for f in selected) if selected else '',
                    'calories': meal_macros['calories'],
                    'protein_g': meal_macros['protein_g'],
                    'carbs_g': meal_macros['carbs_g'],
                    'fats_g': meal_macros['fats_g'],
                    'category': 'veg' if all(f.category == 'veg' for f in selected) else 'non-veg',
                }
                day_data['meals'][meal_type] = {
                    'combined': combined,
                    'target_calories': target_cal,
                }
                for key in daily_macros:
                    daily_macros[key] += meal_macros.get(key, 0)

            day_data['daily_macros'] = daily_macros
            weekly_plan.append(day_data)

            total_kcal += daily_macros['calories']
            total_protein += daily_macros['protein_g']
            total_carbs += daily_macros['carbs_g']
            total_fats += daily_macros['fats_g']

        # Weekly averages for this goal
        avg_kcal = round(total_kcal / 7)
        avg_protein = round(total_protein / 7, 1)
        avg_carbs = round(total_carbs / 7, 1)
        avg_fats = round(total_fats / 7, 1)

        protein_cal = avg_protein * 4
        carbs_cal = avg_carbs * 4
        fats_cal = avg_fats * 9
        total_cal = protein_cal + carbs_cal + fats_cal
        if total_cal > 0:
            protein_pct = round((protein_cal / total_cal) * 100)
            carbs_pct = round((carbs_cal / total_cal) * 100)
            fats_pct = round((fats_cal / total_cal) * 100)
        else:
            protein_pct = carbs_pct = fats_pct = 0

        weekly_avg = {
            'avg_kcal': avg_kcal,
            'protein_pct': protein_pct,
            'carbs_pct': carbs_pct,
            'fats_pct': fats_pct,
        }

        all_plans[goal_slug] = {
            'weekly_plan': weekly_plan,
            'weekly_avg': weekly_avg,
            'goal_name': goal_obj.name,
        }

    return render(request, 'foodlog.html', {
        'all_plans': all_plans,
        'day_names': day_names,
        'default_goal': 'general_fitness',   # the one shown first
    })

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
    """Public workout library – shows ~30% of General Fitness workouts."""
    general_goal = get_goal_from_string('General Fitness')
    workouts = Workout.objects.filter(goal=general_goal)
    if not workouts.exists():
        workouts = Workout.objects.all()

    # Limit to ~30% of the total
    total_count = workouts.count()
    limit = max(1, int(total_count * 0.4))   # at least 1 item
    workouts = workouts.order_by('?')[:limit]   # random subset

    return render(request, 'workout.html', {'workouts': workouts})

def yoga(request):
    """Public yoga library – shows ~30% of General Fitness yoga sessions."""
    general_goal = get_goal_from_string('General Fitness')
    yogas = Yoga.objects.filter(goal=general_goal)
    if not yogas.exists():
        yogas = Yoga.objects.all()

    # Limit to ~30% of the total
    total_count = yogas.count()
    limit = max(1, int(total_count * 0.4))
    yogas = yogas.order_by('?')[:limit]

    return render(request, 'yoga.html', {'yogas': yogas})
