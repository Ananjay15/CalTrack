import random
from datetime import date
from apps.main.models import Goal, Level
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.main.models import Workout, Yoga, Food
from apps.main.services.helpers import (
    calculate_calories,
    split_meal_calories,
    calculate_macros,
    get_goal_from_string,
)


@login_required
def dashboard(request):
    try:
        profile = request.user.profile
    except Exception:
        return render(request, 'dashboard/dashboard.html', {
            'error': 'Please complete your profile first.'
        })


    def _safe_thumbnail(field):
        """Return the image URL from CloudinaryField, ImageField, or plain string."""
        if field is None:
            return None
        if hasattr(field, 'url'):
            return field.url
        if isinstance(field, str):
            return field
        return None
    
    # 1. Calorie data (for profile section)
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

    # 2. Deterministic daily diet plan (same all day)
    goal_obj = profile.goal if profile.goal else get_goal_from_string('General Fitness')
    target_daily = calorie_data['target_calories'] if calorie_data else (profile.target_calories or 2000)
    diet_pref = getattr(profile, 'diet_preference', 'both') or 'both'
    meal_budgets = split_meal_calories(target_daily)

    today = date.today()
    random.seed(today.toordinal())   # same seed → same plan all day

    diet_plan = {}
    total_macros = {'protein_g': 0, 'carbs_g': 0, 'fats_g': 0, 'calories': 0}

    for meal_type, target_cal in meal_budgets.items():
        foods = Food.objects.filter(goal=goal_obj, meal_type__slug=meal_type)
        if diet_pref in ('veg', 'non-veg'):
            foods = foods.filter(category=diet_pref)

        if not foods.exists():
            foods = Food.objects.filter(meal_type__slug=meal_type)
            if diet_pref in ('veg', 'non-veg'):
                foods = foods.filter(category=diet_pref)

        foods_list = list(foods.order_by('id'))
        selected_foods = random.sample(foods_list, min(2, len(foods_list))) if foods_list else []

        meal_macros = calculate_macros(selected_foods)
        diet_plan[meal_type] = {
            'target_calories': target_cal,
            'foods': [{
                'id': f.id,
                'name': f.name,
                'calories': f.total_calories,
                'protein_g': f.protein_g,
                'carbs_g': f.carbs_g,
                'fats_g': f.fats_g,
                'category': f.category,
                'thumbnail':_safe_thumbnail(f.thumbnail),
                'youtube_link': f.youtube_link,
            } for f in selected_foods],
            'macros': meal_macros,
        }
        for key in total_macros:
            total_macros[key] += meal_macros.get(key, 0)

    diet_plan['daily_macros'] = total_macros
    protein_target = round((target_daily * 0.3) / 4, 1) if target_daily else 0

    # 3. Fitness sections (Home Workouts, Gym Workouts, Yoga) – up to 4 each
    level_slug = profile.level.slug if profile.level else 'beginner'

    def _get_intensity(cal_per_min):
        if cal_per_min < 5:
            return 'Low'
        elif cal_per_min < 10:
            return 'Medium'
        elif cal_per_min < 15:
            return 'High'
        else:
            return 'Ultra'

    # Home Workouts
    home_qs = Workout.objects.filter(
        goal=goal_obj, level__slug=level_slug, home_gym__in=['home', 'both']
    )
    if not home_qs.exists():
        home_qs = Workout.objects.filter(goal=goal_obj, home_gym__in=['home', 'both'])
    if not home_qs.exists():
        home_qs = Workout.objects.filter(home_gym__in=['home', 'both'])
    home_workouts = list(home_qs.order_by('?')[:4])

    # Gym Workouts
    gym_qs = Workout.objects.filter(
        goal=goal_obj, level__slug=level_slug, home_gym__in=['gym', 'both']
    )
    if not gym_qs.exists():
        gym_qs = Workout.objects.filter(goal=goal_obj, home_gym__in=['gym', 'both'])
    if not gym_qs.exists():
        gym_qs = Workout.objects.filter(home_gym__in=['gym', 'both'])
    gym_workouts = list(gym_qs.order_by('?')[:4])

    # Yoga
    yoga_qs = Yoga.objects.filter(goal=goal_obj, level__slug=level_slug)
    if not yoga_qs.exists():
        yoga_qs = Yoga.objects.filter(goal=goal_obj)
    if not yoga_qs.exists():
        yoga_qs = Yoga.objects.all()
    yoga_sessions = list(yoga_qs.order_by('?')[:4])

    # Convert to template-friendly dicts
    def workout_to_card(w):
        return {
            'name': w.name,
            'description': w.description,
            'duration_minutes': w.duration_minutes,
            'intensity': _get_intensity(w.calories_burned_per_minute),
            'thumbnail': _safe_thumbnail(w.thumbnail),
            'youtube_link': w.youtube_link,
        }

    def yoga_to_card(y):
        return {
            'name': y.name,
            'description': y.description,
            'duration_minutes': y.duration_minutes,
            'intensity': _get_intensity(y.calories_burned_per_minute),
            'thumbnail': _safe_thumbnail(y.thumbnail),
            'youtube_link': y.youtube_link,
        }

    home_workouts = [workout_to_card(w) for w in home_workouts]
    gym_workouts = [workout_to_card(w) for w in gym_workouts]
    yoga_sessions = [yoga_to_card(y) for y in yoga_sessions]
    goals = Goal.objects.all()
    levels = Level.objects.all()

    context = {
        'profile': profile,
        'diet_data': diet_plan,
        'calorie_data': calorie_data,
        'protein_target': protein_target,
        'today': today,
        'home_workouts': home_workouts,
        'gym_workouts': gym_workouts,
        'yoga_sessions': yoga_sessions,
        'goals': goals,
        'levels': levels,
    }
    return render(request, 'dashboard/dashboard.html', context)