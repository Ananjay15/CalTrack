from django.db import models
from django.contrib.auth.models import User
from apps.main.models import Goal, Level

class Profile(models.Model):
    
    HOME_GYM_CHOICES = [
        ('home', 'Home'),
        ('gym', 'Gym'),
    ]
    DIET_CHOICES = [
        ('veg', 'Vegetarian'),
        ('non-veg', 'Non-Vegetarian'),
        ('both', 'Both'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    ACTIVITY_CHOICES = [
        (1.2, 'Sedentary (little or no exercise)'),
        (1.375, 'Lightly active (1-3 days/week)'),
        (1.55, 'Moderately active (3-5 days/week)'),
        (1.725, 'Very active (6-7 days/week)'),
        (1.9, 'Super active (physical job/twice daily)'),
    ]
    
    
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
        choices=HOME_GYM_CHOICES,
        blank=True, null=True,
        help_text = "Preferred workout location"
    )
    
    diet_preference = models.CharField(
        max_length=10,
        choices=DIET_CHOICES,
        default='both',
        help_text="Dietary preference"
    )
    
    current_weight_kg = models.FloatField(
        null=True, blank=True
        )
    
    height_cm = models.FloatField(
        null=True, blank=True
        )
    
    age = models.PositiveIntegerField(
        null=True, blank=True
        )
    
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True, null=True
        )
    
    activity_level = models.FloatField(
        choices=ACTIVITY_CHOICES,
        null=True, blank=True
        )

    
    
    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.user.username

# Create your models here.
