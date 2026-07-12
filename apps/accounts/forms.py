from django import forms
from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'goal', 'target_calories',
            'level', 'home_gym_preference',
            'yoga_level', 'diet_preference',
            'current_weight_kg', 'height_cm', 'age',
            'gender', 'activity_level',
        ]
        widgets = {
            'goal': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'yoga_level': forms.Select(attrs={'class': 'form-select'}),
            'home_gym_preference': forms.Select(attrs={'class': 'form-select'}),
            'diet_preference': forms.Select(attrs={'class': 'form-select'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'activity_level': forms.Select(attrs={'class': 'form-select'}),
            'target_calories': forms.NumberInput(attrs={'class': 'form-control'}),
            'current_weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'height_cm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
        }