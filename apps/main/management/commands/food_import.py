import csv, os
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.main.models import Food, Goal, MealType

class Command(BaseCommand):
    help = 'Import foods/meals from diet.csv'

    def handle(self, *args, **options):
        base = os.path.join(settings.BASE_DIR, 'data')
        file_path = os.path.join(base, 'diet.csv')
        if not os.path.exists(file_path):
            self.stderr.write(f'Missing file: {file_path}')
            return

        # Try different encodings
        encodings = ['utf-8-sig', 'latin-1']
        data = None
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    reader = csv.DictReader(f)
                    data = list(reader)
                break
            except UnicodeDecodeError:
                continue

        if data is None:
            self.stderr.write(f'Failed to decode {file_path} with any encoding.')
            return

        for row in data:
            goal, _ = Goal.objects.get_or_create(
                slug=row['goal_slug'],
                defaults={'name': row['goal_slug']}
            )
            meal_type, _ = MealType.objects.get_or_create(
                slug=row['meal_type_slug'],
                defaults={'name': row['meal_type_slug']}
            )
            Food.objects.create(
                name=row['name'],
                description=row.get('description', ''),
                total_calories=int(row['total_calories']),
                protein_g=float(row['protein_g']),
                carbs_g=float(row['carbs_g']),
                fats_g=float(row['fats_g']),
                goal=goal,
                meal_type=meal_type,
                category=row.get('category', 'veg'),
                thumbnail=row.get('thumbnail') or None,
                youtube_link=row.get('youtube_link') or None
            )
        self.stdout.write(self.style.SUCCESS('Foods imported'))