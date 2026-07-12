from apps.main.models import Yoga
from django.db.models import F
from .helpers import get_goal_from_string, greedy_workout_selector


def get_yoga_queryset(goal_slug=None, level_slug=None, style_slug=None):
    qs = Yoga.objects.all()
    if goal_slug:
        qs = qs.filter(goal__slug=goal_slug)
    if level_slug:
        qs = qs.filter(level__slug=level_slug)
    if style_slug:
        qs = qs.filter(style__slug=style_slug)
    return qs


def recommend_yoga(user_profile):
    goal_obj = user_profile.goal if user_profile.goal else get_goal_from_string('General Fitness')
    level_slug = (user_profile.yoga_level.slug
                  if hasattr(user_profile, 'yoga_level') and user_profile.yoga_level
                  else 'beginner')

    yoga_qs = get_yoga_queryset(goal_slug=goal_obj.slug, level_slug=level_slug)
    if not yoga_qs.exists():
        yoga_qs = get_yoga_queryset(goal_slug=goal_obj.slug)
    if not yoga_qs.exists():
        return {'yoga': [], 'total_burn': 0, 'target_burn': None}

    target_burn = getattr(user_profile, 'target_burn_yoga', None)
    if target_burn:
        yoga_qs = yoga_qs.annotate(total_burn=F('duration_minutes') * F('calories_burned_per_minute'))
        selected, total_burn = greedy_workout_selector(yoga_qs, target_burn)
        result = [{
            'id': y['workout'].id,
            'name': y['workout'].name,
            'description': y['workout'].description,
            'duration_minutes': y['workout'].duration_minutes,
            'burn': round(y['burn'], 2),
            'thumbnail_url': y['workout'].thumbnail.url if y['workout'].thumbnail else None,
            'youtube_link': y['workout'].youtube_link,
        } for y in selected]
        return {'yoga': result, 'total_burn': round(total_burn, 2), 'target_burn': target_burn}

    yoga_qs = yoga_qs.annotate(burn=F('duration_minutes') * F('calories_burned_per_minute')).order_by('-burn')
    result = [{
        'id': y.id,
        'name': y.name,
        'description': y.description,
        'duration_minutes': y.duration_minutes,
        'burn': round(y.burn, 2),
        'thumbnail_url': y.thumbnail.url if y.thumbnail else None,
        'youtube_link': y.youtube_link,
    } for y in yoga_qs[:10]]
    return {'yoga': result, 'total_burn': None, 'target_burn': None}