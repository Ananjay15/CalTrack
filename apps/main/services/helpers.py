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
        distribution ={
            'breakfast': 0.25,
            'lunch': 0.35,
            'snack': 0.10,
            'dinner': 0.30,
        }
    return {meal: round(target_daily_calories * pct) for meal, pct in distribution.items()}