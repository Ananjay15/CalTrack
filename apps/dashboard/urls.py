from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # path('chat/', chat_views.chat_assistant, name='chat_assistant'),
    # path('chart/calories/', views.calorie_chart_data, name='calorie_chart_data'),
    # path('log/food/<int:food_id>/', views.log_food, name='log_food'),
    # path('log/workout/<int:workout_id>/', views.log_workout, name='log_workout'),
    # path('log/yoga/<int:yoga_id>/', views.log_yoga, name='log_yoga'),
]