from apps.main.models import Food
from apps.main.services.helpers import (
    get_goal_from_string,
    split_meal_calories,
    greedy_food_selector,
    calculate_macros,
    calculate_calories,
)


def get_food_queryset(goal_slug=None, meal_type_slug=None, diet_preference='both'):
    qs = Food.objects.all()
    if goal_slug:
        qs = qs.filter(goal__slug=goal_slug)
    if meal_type_slug:
        qs = qs.filter(meal_type__slug=meal_type_slug)
    if diet_preference in ('veg', 'non-veg'):
        qs = qs.filter(category=diet_preference)
    return qs


def recommend_diet(user_profile):
    goal_obj = user_profile.goal if user_profile.goal else get_goal_from_string('General Fitness')

    # Determine daily calorie target
    if (user_profile.age and user_profile.gender and
        user_profile.height_cm and user_profile.current_weight_kg and
        user_profile.activity_level):
        data = calculate_calories(
            age=user_profile.age,
            gender=user_profile.gender,
            height=user_profile.height_cm,
            weight=user_profile.current_weight_kg,
            activity=user_profile.activity_level,
            goal=goal_obj
        )
        target_daily = data['target_calories']
    else:
        target_daily = getattr(user_profile, 'target_calories', 2000) or 2000

    diet_pref = getattr(user_profile, 'diet_preference', 'both') or 'both'
    meal_calories = split_meal_calories(target_daily)

    plan = {}
    total_macros = {'protein_g': 0, 'carbs_g': 0, 'fats_g': 0, 'calories': 0}

    for meal_type, target_cal in meal_calories.items():
        # 1. Try to get foods matching goal + meal type + diet preference
        foods = get_food_queryset(
            goal_slug=goal_obj.slug,
            meal_type_slug=meal_type,
            diet_preference=diet_pref,
        )

        # 2. If none found, try without the goal filter
        if not foods.exists():
            foods = get_food_queryset(
                meal_type_slug=meal_type,
                diet_preference=diet_pref,
            )

        # 3. If still none, fall back to all foods of that meal type (ignoring goal & diet)
        if not foods.exists():
            foods = Food.objects.filter(meal_type__slug=meal_type)

        # Ensure we never pass None to greedy_food_selector
        if foods is None:
            foods = Food.objects.none()

        selected_foods, gap = greedy_food_selector(foods, target_cal)
        meal_macros = calculate_macros(selected_foods)
        plan[meal_type] = {
            'target_calories': target_cal,
            'foods': [{
                'id': f.id,
                'name': f.name,
                'description': f.description,
                'calories': f.total_calories,
                'protein_g': f.protein_g,
                'carbs_g': f.carbs_g,
                'fats_g': f.fats_g,
                'thumbnail_url': f.thumbnail.url if f.thumbnail else None,
                'youtube_link': f.youtube_link,
                'category': f.category,
            } for f in selected_foods],
            'macros': meal_macros,
            'gap': round(gap, 2),
        }
        for key in total_macros:
            total_macros[key] += meal_macros.get(key, 0)

    plan['daily_macros'] = total_macros
    return plan