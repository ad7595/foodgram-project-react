import json

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('data/ingredients.json', encoding='utf-8',
                  ) as ingredients_data_file:
            data = json.load(ingredients_data_file)
            for i in range(len(data)):
                Ingredient.objects.get_or_create(
                    name=data[i].get('name'),
                    measurement_unit=data[i].get('measurement_unit')
                )
        print('Импорт выполнен')
