from django.db import models
from cloudinary.models import CloudinaryField

# Create your models here.
class Goal(models.Model):
    name = models.CharField(max_length=100, unique =True)
    slug = models.SlugField(max_length=100, unique =True)
    
    class Meta:
        verbose_name = "Goal"
        verbose_name_plural = "Goals"

    def __str__(self):
        return self.name
    
class Level(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    
    class Meta:
        verbose_name = "Fitness Level"
        verbose_name_plural = "Fitness Levels"
    
    def __str__(self):
        return self.name
    

class MealType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    
    class Meta:
        verbose_name = "Meal Type"
        verbose_name_plural = "Meal Types"

    def __str__(self):
        return self.name
    
 
# ---------- Core Recommendation Models ----------   
    
class Workout(models.Model):
    HOME_GYM_CHOICES = [
        ('home', 'Home'),
        ('gym', 'Gym'),
        ('both', 'Both'),
    ]
    
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(help_text="Average duration (minutes)")
    calories_burned_per_minute = models.FloatField(help_text="Avg. calories burned per minute")
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    home_gym = models.CharField(max_length=10, choices=HOME_GYM_CHOICES, default='both' )
    thumbnail = CloudinaryField('images', blank=True, null=True)
    youtube_link = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Workout"
        verbose_name_plural = "Workouts"
        
    def __str__(self):
        return self.name
    
class Yoga(models.Model):
    TYPE_CHOICES = [
        ('seated','Seated'),
        ('standing','Standing'),
        ('forward-bend','Forward-bend'),
        ('back-bend','Back-bend'),
        ('twist','Twist'),
        ('inversion','Inversion'),
        ('arm-balance','Arm-balance'),
        ('Restorative','Restorative'),
        ('Preparatory','Preparatory')
    ]
    
    name = models.CharField(max_length=120)
    sanskrit_name = models.CharField(max_length=120, blank=True, help_text="Sanskrit name of yoga poses")
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField()
    calories_burned_per_minute = models.FloatField()
    pose_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='')
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    thumbnail = models.URLField(blank=True, null=True)
    youtube_link = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "Yoga Pose"
        verbose_name_plural = "Yoga Poses"

    def __str__(self):
        return self.name
    
class Food(models.Model):
    CATEGORY_CHOICES = [
        ('veg', 'Veg'),
        ('non-veg', 'Non-Veg '),
    ]  
    
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, help_text="Meal components / dish description")
    total_calories = models.PositiveIntegerField()
    protein_g = models.FloatField(default=0)
    carbs_g = models.FloatField(default=0)
    fats_g = models.FloatField(default=0)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    meal_type = models.ForeignKey(MealType, on_delete=models.CASCADE)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    thumbnail = models.URLField(blank=True, null=True)
    youtube_link = models.URLField(blank=True, null=True, help_text="Recipe video link")

    class Meta:
        verbose_name = "Food / Meal"
        verbose_name_plural = "Foods / Meals"

    def __str__(self):
        return f"{self.name} ({self.total_calories} kcal)"