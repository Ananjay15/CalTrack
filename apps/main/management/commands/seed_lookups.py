from django.core.management.base import BaseCommand
from apps.main.models import Goal, Level, YogaStyle, MealType

class Command(BaseCommand):
    help = 'Create default lookup data'

    def handle(self, *args, **options):
        goals = [
            ('Weight Loss', 'weight_loss'),
            ('Muscle Gain', 'muscle_gain'),
            ('Maintenance', 'maintenance'),
            ('General Fitness', 'general_fitness'),
 
        ]
        for name, slug in goals:
            Goal.objects.get_or_create(slug=slug, defaults={'name': name})

        for name in ['Beginner', 'Intermediate', 'Advanced']:
            Level.objects.get_or_create(slug=name.lower(), defaults={'name': name})

        for name in ['Hatha', 'Vinyasa', 'Ashtanga', 'Yin', 'Restorative', 'Prenatal', 'Chair', 'Kundalini', 'Bikram', 'Iyengar', 'Acro', 'Nidra', 'Pranayama', 'Sculpt', 'Kids']:
            YogaStyle.objects.get_or_create(slug=name.lower(), defaults={'name': name})

        for name in ['Breakfast', 'Lunch', 'Snack', 'Dinner']:
            MealType.objects.get_or_create(slug=name.lower(), defaults={'name': name})

        self.stdout.write(self.style.SUCCESS('Lookups seeded'))