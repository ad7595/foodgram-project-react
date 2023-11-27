import os
import json
from django.core.management import BaseCommand
from django.conf import settings
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(os.path.join(settings.BASE_DIR, 'data', 'ingredients.json'),
                  'r', encoding='utf-8') as ingredients_data_file:
            data = json.load(ingredients_data_file)
            for i in range(len(data)):
                Ingredient.objects.get_or_create(
                    name=data[i].get('name'),
                    measurement_unit=data[i].get('measurement_unit')
                )
            print('Импорт выполнен.')
