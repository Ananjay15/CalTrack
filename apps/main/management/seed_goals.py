from django.core.management.base import BaseCommand
from apps.main.models import Goal

class Command(BaseCommand):
    help = "Create default fitness goal"
    
    def handle(self, *args, **options):
        goals = [
            ('Weight Loss', 'weight_loss'),
            ('Muscle Gain', 'muscle_gain'),
            ('General Fitness', 'general_fitness'),
        ]
        for name, slug in goals:
            Goal.objects.get_or_create(slug=slug, defaults={'name':name})
        self.stdout.write(self.style.SUCCESS('Soals seeded'))