from django.contrib import admin
from .models import Goal, Level, YogaStyle, MealType, Workout, Yoga, Food

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(YogaStyle)
class YogaStyleAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(MealType)
class MealTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ['name', 'goal', 'level', 'duration_minutes', 'home_gym']
    list_filter = ['goal', 'level', 'home_gym']
    search_fields = ['name']

@admin.register(Yoga)
class YogaAdmin(admin.ModelAdmin):
    list_display = ['name', 'goal', 'level', 'style', 'duration_minutes']
    list_filter = ['goal', 'level', 'style']

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'goal', 'meal_type', 'category', 'total_calories']
    list_filter = ['goal', 'meal_type', 'category']
