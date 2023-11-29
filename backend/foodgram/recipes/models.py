from colorfield import fields
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

MIN_AMOUNT = 1
MIN_COOKING_TIME = 1

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингридиента."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = 'name'
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Модель тэгов."""
    name = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name='Тэг'
    )
    color = fields.ColorField(
        max_length=7,
        unique=True,
        format='hex',
        verbose_name='HEX-код'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        blank=False,
        verbose_name='Картинка'
    )
    text = models.TextField(
        help_text='Описание рецепта',
        verbose_name='Описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время готовки',
        validators=MinValueValidator(
                MIN_COOKING_TIME, message='Время готовки минимум 1 минута!'
            ),
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    """Модель связывающая ингредиенты и рецепты."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=MinValueValidator(MIN_AMOUNT),
        verbose_name='Количество'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='recipe_ingredient',
            )
        ]

    def __str__(self) -> str:
        return f'{self.ingredient}'


# class RecipeTag(models.Model):
#     """Модель связывающая тэги и рецепты."""
#     recipe = models.ForeignKey(
#         Recipe,
#         on_delete=models.CASCADE,
#         verbose_name='Рецепт'
#     )
#     tag = models.ForeignKey(
#         Tag,
#         on_delete=models.CASCADE,
#         verbose_name='Тег'
#     )

#     class Meta:
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['recipe', 'tag'],
#                 name='recipe_tag_unique'
#             )
#         ]


class Favorite(models.Model):
    """Модель избранного."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='favourite'
            )
        ]

    def __str__(self):
        return f'Добавлен "{self.recipe}" в Избранное'


class ShoppingCart(models.Model):
    """Модель корзины."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Корзина',
        verbose_name_plural = 'Корзина',
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='user_shoppingcart'
            )
        ]

    def __str__(self):
        return f'"{self.recipe}" добавлен в Корзину покупок'
