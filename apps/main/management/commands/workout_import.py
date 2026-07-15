import csv, os
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.main.models import Workout, Goal, Level

class Command(BaseCommand):
    help = 'Import workouts from workouts.csv (ignores thumbnail column)'

    def handle(self, *args, **options):
        base = os.path.join(settings.BASE_DIR, 'data')
        file_path = os.path.join(base, 'workout.csv')
        if not os.path.exists(file_path):
            self.stderr.write(f'Missing file: {file_path}')
            return

        with open(file_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                goal, _ = Goal.objects.get_or_create(
                    slug=row['goal_slug'],
                    defaults={'name': row['goal_slug']}
                )
                level, _ = Level.objects.get_or_create(
                    slug=row['level_slug'],
                    defaults={'name': row['level_slug']}
                )
                Workout.objects.create(
                    name=row['name'],
                    description=row['description'],
                    duration_minutes=int(row['duration_minutes']),
                    calories_burned_per_minute=float(row['calories_burned_per_minute']),
                    goal=goal,
                    level=level,
                    home_gym=row['home_gym'],
                    youtube_link=row.get('youtube_link') or None,
                    # thumbnail is NOT set here – it will stay NULL
                )
        self.stdout.write(self.style.SUCCESS('Workouts imported'))