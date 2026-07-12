from django.db.models import QuerySet, F
from apps.main.models import Workout, Food, Goal

def calculate_workout_burn(workout: Workout) -> float:
    
    return workout.duration_minutes * workout.calories_burned_per_minute

def calculate_yoga_burn(yoga) -> float:
    
    return yoga.duration_minutes * yoga.calories_burned_per_minute

def split_meal_calories(
    target_daily_calories: int,
    distribution: dict = None,
) -> dict:
    if distribution is None:
        distribution = {
            'breakfast': 0.25,
            'lunch': 0.35,
            'snack': 0.10,
            'dinner': 0.30,
        }
    return {meal: round(target_daily_calories * pct) for meal, pct in distribution.items()}


def greedy_workout_selector(workouts, target_burn: float) -> tuple:
    selected = []
    total = 0.0
    workouts = workouts.annotate(
        total_burn=F('duration_minutes') * F('calories_burned_per_minute')
    ).order_by('-total_burn')
    for w in workouts:
        total += w.total_burn
        selected.append({'workout':w, 'burn':w.total_burn})
        if total >= target_burn:
            break
    return selected, total


def greedy_food_selector(foods, target_calories: float) -> tuple:
    selected = []
    remaining = target_calories
    for food in foods.order_by('total_calories'):
        if food.total_calories <= remaining:
            selected.append(food)
            remaining -= food.total_calories
        if remaining <= 0:
            break    
    return selected, remaining


def calculate_macros(foods: list) -> dict:
    return{
        'protein_g': sum(f.protein_g for f in foods),
        'carbs_g': sum(f.carbs_g for f in foods),
        'fats_g': sum(f.fats_g for f in foods),
        'calories': sum(f.total_calories for f in foods),
    }
 
    
def get_goal_from_string(goal_name: str) -> Goal:
    goal_name = goal_name.strip().lower()
    goal = Goal.objects.filter(name__iexact=goal_name).first()
    if not goal:
        goal = Goal.objects.filter(slug=goal_name).first()
    if not goal:
        goal, _ = Goal.objects.get_or_create(
            slug = 'general_fitness',
            defaults={'name': 'General Fitness'}
        )
    return goal

def calculate_calories(
    age,
    gender,
    height,
    weight,
    activity,
    goal
):
    bmi = weight / ((height / 100) ** 2)
    
    if bmi < 18.5:
        bmi_status = "Underweight"
    elif bmi < 25:
        bmi_status = "Healthy Weight"
    elif bmi < 30:
        bmi_status = "Overweight"
    else:
        bmi_status = "Obese"
    
    if gender == 'male':
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        
    maintenance = bmr * activity
    
    goal_slug = goal.slug if hasattr(goal, 'slug') else str(goal).lower()
    if goal_slug in ("weight_loss", "weight loss"):
        target_calories = maintenance - 300
        recommendation = "Weight Loss"
    elif goal in ("muscle_gain","muscle gain") :
        target_calories = maintenance + 300 
        recommendation = "Muscle Gain"
    else:
        target_calories = maintenance
        recommendation = "Maintenance"
        
    return{
        'bmi': round(bmi,1),
        'bmr': round(bmr),
        'target_calories': round(target_calories),
        'recommendation': recommendation,
        'bmi_status': bmi_status,
    }