import json
from pathlib import Path
from django.core.management.base import BaseCommand
from apps.main.models import Workout

class Command(BaseCommand):
    help = 'Link uploaded Cloudinary thumbnails to workouts based on title matching'

    def handle(self, *args, **options):
        # Path to the JSON results file from your upload script
        script_dir = Path(__file__).resolve().parent.parent.parent.parent.parent   # adjust if needed
        json_file = script_dir / 'data' / 'workout_upload_results.json'   # or wherever you store it

        if not json_file.exists():
            self.stderr.write(f'JSON file not found: {json_file}')
            return

        with json_file.open('r', encoding='utf-8') as f:
            results = json.load(f)

        updated_count = 0
        skipped_count = 0
        for item in results:
            if item['status'] != 'success':
                skipped_count += 1
                continue

            title = item['title']
            public_id = item['public_id']

            # Try to find a workout whose name (case-insensitive) matches the title
            workouts = Workout.objects.filter(name__iexact=title)
            if not workouts.exists():
                # Try matching by slugified name (the script's slugify function)
                # We'll just print a warning and continue
                self.stderr.write(f'No workout found for title: {title}')
                skipped_count += 1
                continue

            # If multiple workouts have the same name (unlikely), update all
            for workout in workouts:
                workout.thumbnail = public_id
                workout.save(update_fields=['thumbnail'])
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Updated {updated_count} workouts. Skipped {skipped_count} entries.'
        ))