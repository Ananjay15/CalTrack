from apps.main.models import Workout
from .helpers import greedy_workout_selector, get_goal_from_string, calculate_calories


def get_workout_queryset(goal_slug=None, level_slug=None, home_gym=None):
    qs = Workout.objects.all()
    if goal_slug:
        qs = qs.filter(goal__slug=goal_slug)
    if level_slug:
        qs = qs.filter(level__slug=level_slug)
    if home_gym:
        qs = qs.filter(home_gym__in=[home_gym, 'both'])
    return qs


def calculate_target_burn(user_profile) -> float:
    """
    Use profile metrics if available, else fallback to fixed values.
    """
    if not (user_profile.age and user_profile.gender and
            user_profile.height_cm and user_profile.current_weight_kg and
            user_profile.activity_level and user_profile.goal):
        goal_slug = user_profile.goal.slug if user_profile.goal else 'general_fitness'
        if goal_slug == 'weight_loss':
            return 400.0
        elif goal_slug == 'muscle_gain':
            return 200.0
        return 250.0

    data = calculate_calories(
        age=user_profile.age,
        gender=user_profile.gender,
        height=user_profile.height_cm,
        weight=user_profile.current_weight_kg,
        activity=user_profile.activity_level,
        goal=user_profile.goal
    )
    if data['recommendation'] == 'Weight Loss':
        return 300.0
    elif data['recommendation'] == 'Muscle Gain':
        return 150.0
    return 200.0


def recommend_workout(user_profile):
    goal_obj = user_profile.goal if user_profile.goal else get_goal_from_string('General Fitness')
    level_slug = user_profile.level.slug if user_profile.level else 'beginner'
    home_gym = getattr(user_profile, 'home_gym_preference', None)

    workouts = get_workout_queryset(
        goal_slug=goal_obj.slug,
        level_slug=level_slug,
        home_gym=home_gym,
    )
    if not workouts.exists():
        workouts = get_workout_queryset(goal_slug=goal_obj.slug, home_gym=home_gym)
    if not workouts.exists():
        return {'workouts': [], 'total_burn_achieved': 0, 'target_burn': calculate_target_burn(user_profile)}

    target_burn = calculate_target_burn(user_profile)
    selected_list, total_burn = greedy_workout_selector(workouts, target_burn)

    result = []
    for item in selected_list:
        w = item['workout']
        result.append({
            'id': w.id,
            'name': w.name,
            'description': w.description,
            'duration_minutes': w.duration_minutes,
            'burn': round(item['burn'], 2),
            'thumbnail_url': w.thumbnail.url if w.thumbnail else None,
            'youtube_link': w.youtube_link,
        })
    return {
        'workouts': result,
        'total_burn_achieved': round(total_burn, 2),
        'target_burn': target_burn,
    }