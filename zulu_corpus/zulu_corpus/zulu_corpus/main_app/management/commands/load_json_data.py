# main_app/management/commands/load_json_data.py
from django.core.management.base import BaseCommand
from main_app.utils.json_loader import load_words_from_json

class Command(BaseCommand):
    help = 'Load word data from JSON file'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading',
        )
    
    def handle(self, *args, **options):
        self.stdout.write('Loading data from JSON file...')
        
        result = load_words_from_json()
        
        if 'error' in result:
            self.stdout.write(
                self.style.ERROR(f'Error: {result["error"]}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully loaded data: {result["words_created"]} words created, '
                    f'{result["words_updated"]} words updated, '
                    f'{result["pairs_created"]} word pairs created'
                )
            )