from django.contrib import admin
from .models import Goal, Level, MealType, Workout, Yoga, Food

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
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
    list_display = ['name', 'sanskrit_name', 'pose_type', 'goal', 'level', 'duration_minutes']
    list_filter = ['goal', 'level', 'pose_type']
    search_fields = ['name', 'sanskrit_name', 'description']
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'sanskrit_name', 'pose_type', 'description')}),
        ('Metrics', {'fields': ('duration_minutes', 'calories_burned_per_minute')}),
        ('Classification', {'fields': ('goal', 'level')}),
        ('Media', {'fields': ('thumbnail', 'youtube_link')}),
    )

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'goal', 'meal_type', 'category', 'total_calories']
    list_filter = ['goal', 'meal_type', 'category']
