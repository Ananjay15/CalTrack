from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    
    goal = models.CharField(
        max_length=100
    )
    
    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.user.username

# Create your models here.
