from django.urls import  path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('diet/', views.diet, name = 'diet'),
    path('caloriescalculator/', views.calculator, name = 'calculator'),
    path('workout/', views.workout, name = 'workout'),
    path('yoga/', views.yoga, name = 'yoga'),
    
]