import csv, os
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.main.models import Goal, Level, Yoga


class Command(BaseCommand):
    help = "Importing data of meals from CSV files (creates missing lookups)"
    
    def handle(self, *args, **options):
        
        base = os.path.join(settings.BASE_DIR,"data")
        
               # ---------- Yoga ----------
        file_path = os.path.join(base, 'yoga.csv')
        if not os.path.exists(file_path):
            self.stderr.write(f'Missing file: {file_path}')
        else:
            with open(file_path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    goal, _ = Goal.objects.get_or_create(
                        slug=row['goal_slug'],
                        defaults={'name': row['goal_slug']}
                    )
                    # Level is just the slug (e.g., "beginner", "intermediate")
                    level, _ = Level.objects.get_or_create(
                        slug=row['level'],
                        defaults={'name': row['level'].capitalize()}
                    )
                    Yoga.objects.create(
                        name=row['name'],
                        sanskrit_name=row.get('sanskrit_name', ''),
                        pose_type=row.get('pose_type', ''),
                        description=row['description'],
                        duration_minutes=int(row['duration_minutes']),
                        calories_burned_per_minute=float(row['calories_burned_per_minute']),
                        goal=goal,
                        level=level,
                        thumbnail=row.get('thumbnail') or None,
                        youtube_link=row.get('youtube_link') or None
                    )
            self.stdout.write(self.style.SUCCESS('Yoga imported'))
        
    