import random
from datetime import date

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.main.services.workout import recommend_workout
from apps.main.services.yoga import recommend_yoga
from apps.main.services.helpers import (
    calculate_calories,
    split_meal_calories,
    calculate_macros,
    get_goal_from_string,
)
from apps.main.models import Food


@login_required
def dashboard(request):
    try:
        profile = request.user.profile
    except Exception:
        return render(request, 'dashboard/dashboard.html', {
            'error': 'Please complete your profile first.'
        })

    # 1. Workout & Yoga recommendations
    workout_data = recommend_workout(profile)
    yoga_data = recommend_yoga(profile)

    # 2. Calorie data (for profile section)
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

    # 3. Deterministic daily diet plan (same all day)
    goal_obj = profile.goal if profile.goal else get_goal_from_string('General Fitness')
    target_daily = calorie_data['target_calories'] if calorie_data else (profile.target_calories or 2000)
    diet_pref = getattr(profile, 'diet_preference', 'both') or 'both'
    meal_budgets = split_meal_calories(target_daily)

    # Use today's date as seed to make the plan stable all day
    today = date.today()
    random.seed(today.toordinal())   # same seed → same "random" choices all day

    diet_plan = {}
    total_macros = {'protein_g': 0, 'carbs_g': 0, 'fats_g': 0, 'calories': 0}

    for meal_type, target_cal in meal_budgets.items():
        # Filter foods matching goal + meal type + diet preference
        foods = Food.objects.filter(goal=goal_obj, meal_type__slug=meal_type)
        if diet_pref in ('veg', 'non-veg'):
            foods = foods.filter(category=diet_pref)

        if not foods.exists():
            foods = Food.objects.filter(meal_type__slug=meal_type)
            if diet_pref in ('veg', 'non-veg'):
                foods = foods.filter(category=diet_pref)

        # Deterministic pick: sort by id, then use random.sample (seeded) to get 2 items
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
                'youtube_link': f.youtube_link,
            } for f in selected_foods],
            'macros': meal_macros,
        }
        for key in total_macros:
            total_macros[key] += meal_macros.get(key, 0)

    diet_plan['daily_macros'] = total_macros

    # 4. Protein target (from calorie target – 30% of calories / 4)
    protein_target = round((target_daily * 0.3) / 4, 1) if target_daily else 0

    # 5. Balanced fitness data (interleave workouts and yoga)
    workouts = workout_data.get('workouts', [])
    yogas = yoga_data.get('yoga', [])

    combined_fitness = []
    max_len = max(len(workouts), len(yogas))
    for i in range(max_len):
        if i < len(workouts):
            combined_fitness.append({'type': 'workout', 'data': workouts[i]})
        if i < len(yogas):
            combined_fitness.append({'type': 'yoga', 'data': yogas[i]})

    fitness_data = {
        'combined': combined_fitness,
        'workout_count': len(workouts),
        'yoga_count': len(yogas),
    }

    context = {
        'profile': profile,
        'fitness_data': fitness_data,       # use this in the fitness tab
        'diet_data': diet_plan,
        'calorie_data': calorie_data,
        'protein_target': protein_target,
        'today': today,
    }
    return render(request, 'dashboard/dashboard.html', context)