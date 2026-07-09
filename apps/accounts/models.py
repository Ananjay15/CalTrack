from django.db import models
from django.contrib.auth.models import User
from main.models import Goal, Level

class Profile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    goal = models.ForeignKey(
        Goal,
        on_delete =models.SET_NULL,
        null=True, blank=True,
        help_text="Select your primary fitness goal"
    )
    
    target_calories = models.PositiveIntegerField(
        default=2000, help_text="Daily calorie target"
    )
    
    level = models.ForeignKey(
        Level,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='workout_level', 
        help_text="Workout fitness level"
    )
    
    yoga_level =models.ForeignKey(
        Level, 
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='yoga_level',
        help_text="Yoga experience level"
    )
    
    home_gym_preference = models.CharField(
        max_length=10,
        choices=[('home','Home'),('gym','Gym')],
        blank=True, null=True,
        help_text = "Preferred workout location"
    )
    
    diet_preference = models.CharField(
        max_length=10,
        choices=[('veg', 'Vegetarian'), ('non-veg', 'Non-Vegetarian'), ('both', 'Both')],
        default='both',
        help_text="Dietary preference"
    )
    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.user.username

# Create your models here.
