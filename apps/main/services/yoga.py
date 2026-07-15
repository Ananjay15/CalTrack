from django.db.models import F, Value, IntegerField, FloatField
from django.db.models.functions import Coalesce
from apps.main.models import Yoga
from .helpers import get_goal_from_string, greedy_workout_selector


def get_yoga_queryset(goal_slug=None, level_slug=None):
    qs = Yoga.objects.all()
    if goal_slug:
        qs = qs.filter(goal__slug=goal_slug)
    if level_slug:
        qs = qs.filter(level__slug=level_slug)
    return qs


def recommend_yoga(user_profile):
    """
    Recommend yoga sessions based on user profile.
    If duration_minutes or calories_burned_per_minute are missing,
    default values are used (20 min, 3.0 cal/min).
    """
    goal_obj = user_profile.goal if user_profile.goal else get_goal_from_string('General Fitness')
    level_slug = (user_profile.yoga_level.slug
                  if hasattr(user_profile, 'yoga_level') and user_profile.yoga_level
                  else 'beginner')

    yoga_qs = get_yoga_queryset(goal_slug=goal_obj.slug, level_slug=level_slug)
    if not yoga_qs.exists():
        yoga_qs = get_yoga_queryset(goal_slug=goal_obj.slug)
    if not yoga_qs.exists():
        return {'yoga': [], 'total_burn': 0, 'target_burn': None}

    # ----- Safe defaults for missing duration / cal-per-min -----
    yoga_qs = yoga_qs.annotate(
        safe_duration=Coalesce('duration_minutes', Value(20, output_field=IntegerField())),
        safe_cal_per_min=Coalesce(
            'calories_burned_per_minute',
            Value(3.0, output_field=FloatField())
        ),
        burn=F('safe_duration') * F('safe_cal_per_min')
    )

    target_burn = getattr(user_profile, 'target_burn_yoga', None)
    if target_burn:
        selected, total_burn = greedy_workout_selector(yoga_qs, target_burn)
        result = []
        for item in selected:
            y = item['workout']
            result.append({
                'id': y.id,
                'name': y.name,
                'sanskrit_name': getattr(y, 'sanskrit_name', ''),
                'pose_type': getattr(y, 'pose_type', 'asana'),
                'description': y.description,
                'duration_minutes': y.safe_duration,
                'burn': round(item['burn'], 2),
                'thumbnail_url': y.cloudinary_url or (y.thumbnail.url if y.thumbnail else None),
                'youtube_link': y.youtube_link,
            })
        return {
            'yoga': result,
            'total_burn': round(total_burn, 2),
            'target_burn': target_burn,
        }

    # No target_burn_yoga – return top 10 by burn
    yoga_qs = yoga_qs.order_by('-burn')[:10]
    result = []
    for y in yoga_qs:
        result.append({
            'id': y.id,
            'name': y.name,
            'sanskrit_name': getattr(y, 'sanskrit_name', ''),
            'pose_type': getattr(y, 'pose_type', ''),
            'description': y.description,
            'duration_minutes': y.safe_duration,
            'burn': round(y.burn, 2),
            'thumbnail_url': y.cloudinary_url or (y.thumbnail.url if y.thumbnail else None),
            'youtube_link': y.youtube_link,
        })
    return {
        'yoga': result,
        'total_burn': None,
        'target_burn': None,
    }