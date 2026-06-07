from django.urls import  path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('foodlog/', views.foodlog, name = 'foodlog'),
    path('caloriescalculator/', views.calculator, name = 'calculator'),
    path('workout/', views.workout, name = 'workout'),
    path('yoga/', views.yoga, name = 'yoga'),
    
]