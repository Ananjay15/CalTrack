from django.core.management.base import BaseCommand
from apps.main.models import Workout, Yoga, Food
from django.db.models import Count

class Command(BaseCommand):
    help = 'Remove duplicate Workout, Yoga, and Food records'

    def handle(self, *args, **options):
        # Workouts
        duplicates = (
            Workout.objects
            .values('name', 'goal_id', 'level_id')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )
        total_deleted = 0
        for dup in duplicates:
            ids = Workout.objects.filter(
                name=dup['name'],
                goal_id=dup['goal_id'],
                level_id=dup['level_id']
            ).order_by('id').values_list('id', flat=True)[1:]
            Workout.objects.filter(id__in=list(ids)).delete()
            total_deleted += len(ids)
        self.stdout.write(f'Deleted {total_deleted} duplicate workouts')

        # Yoga – similar pattern
        duplicates = (
            Yoga.objects
            .values('name', 'goal_id', 'level_id')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )
        total_deleted = 0
        for dup in duplicates:
            ids = Yoga.objects.filter(
                name=dup['name'],
                goal_id=dup['goal_id'],
                level_id=dup['level_id']
            ).order_by('id').values_list('id', flat=True)[1:]
            Yoga.objects.filter(id__in=list(ids)).delete()
            total_deleted += len(ids)
        self.stdout.write(f'Deleted {total_deleted} duplicate yoga sessions')

        # Food – by name, goal, meal_type
        duplicates = (
            Food.objects
            .values('name', 'goal_id', 'meal_type_id')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )
        total_deleted = 0
        for dup in duplicates:
            ids = Food.objects.filter(
                name=dup['name'],
                goal_id=dup['goal_id'],
                meal_type_id=dup['meal_type_id']
            ).order_by('id').values_list('id', flat=True)[1:]
            Food.objects.filter(id__in=list(ids)).delete()
            total_deleted += len(ids)
        self.stdout.write(f'Deleted {total_deleted} duplicate foods')