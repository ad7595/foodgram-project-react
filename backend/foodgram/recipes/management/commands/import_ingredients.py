import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('data/ingredients.json', encoding='utf-8',
                  ) as ingredients_data_file:
            ingredient_reader = csv.reader(
                ingredients_data_file, delimiter=','
            )
            for ingrideient_row in ingredient_reader:
                Ingredient.objects.get_or_create(
                    name=ingrideient_row[0],
                    measurement_unit=ingrideient_row[1]
                )
        self.stdout.write(self.style.SUCCESS('Импорт выполнен'))
