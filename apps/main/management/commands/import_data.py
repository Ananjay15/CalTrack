import csv, os
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.main.models import Goal, Level, YogaStyle, MealType, Workout, Yoga, Food


class Command(BaseCommand):
    help = 'Import workouts, yoga, and food from CSV files (creates missing lookups)'

    def handle(self, *args, **options):
        base = os.path.join(settings.BASE_DIR, 'data')

        # ---------- Workouts ----------
        file_path = os.path.join(base, 'workout.csv')
        if not os.path.exists(file_path):
            self.stderr.write(f'Missing file: {file_path}')
        else:
            with open(file_path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    goal, _ = Goal.objects.get_or_create(slug=row['goal_slug'], defaults={'name': row['goal_slug']})
                    level, _ = Level.objects.get_or_create(slug=row['level_slug'], defaults={'name': row['level_slug']})
                    Workout.objects.create(
                        name=row['name'],
                        description=row['description'],
                        duration_minutes=int(row['duration_minutes']),
                        calories_burned_per_minute=float(row['calories_burned_per_minute']),
                        goal=goal,
                        level=level,
                        home_gym=row['home_gym'],
                        youtube_link=row.get('youtube_link') or None
                    )
            self.stdout.write(self.style.SUCCESS('Workouts imported'))

        # ---------- Yoga ----------
        file_path = os.path.join(base, 'yoga.csv')
        if not os.path.exists(file_path):
            self.stderr.write(f'Missing file: {file_path}')
        else:
            with open(file_path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    goal, _ = Goal.objects.get_or_create(slug=row['goal_slug'], defaults={'name': row['goal_slug']})
                    level, _ = Level.objects.get_or_create(slug=row['level_slug'], defaults={'name': row['level_slug']})
                    style = None
                    if row.get('style_slug'):
                        style, _ = YogaStyle.objects.get_or_create(
                            slug=row['style_slug'],
                            defaults={'name': row['style_slug']}
                        )
                    Yoga.objects.create(
                        name=row['name'],
                        description=row['description'],
                        duration_minutes=int(row['duration_minutes']),
                        calories_burned_per_minute=float(row['calories_burned_per_minute']),
                        goal=goal,
                        level=level,
                        style=style,
                        youtube_link=row.get('youtube_link') or None
                    )
            self.stdout.write(self.style.SUCCESS('Yoga imported'))

        # ---------- Foods ----------
        file_path = os.path.join(base, 'diet.csv')
        if not os.path.exists(file_path):
            self.stderr.write(f'Missing file: {file_path}')
        else:
            with open(file_path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    goal, _ = Goal.objects.get_or_create(slug=row['goal_slug'], defaults={'name': row['goal_slug']})
                    meal_type, _ = MealType.objects.get_or_create(
                        slug=row['meal_type_slug'],
                        defaults={'name': row['meal_type_slug']}
                    )
                    Food.objects.create(
                        name=row['name'],
                        description=row['description'],
                        total_calories=int(row['total_calories']),
                        protein_g=float(row['protein_g']),
                        carbs_g=float(row['carbs_g']),
                        fats_g=float(row['fats_g']),
                        goal=goal,
                        meal_type=meal_type,
                        category=row['category'],
                        youtube_link=row.get('youtube_link') or None
                    )
            self.stdout.write(self.style.SUCCESS('Foods imported'))