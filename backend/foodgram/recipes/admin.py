from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'id', 'title', 'author', 'in_favorite', 'cooking_time'
    )
    list_editable = ('cooking_time',)
    readonly_fields = ('in_favorites',)
    list_filter = ('title', 'author', 'tags')
    search_fields = ('title', 'author')
    empty_value_display = '-пусто-'

    def in_favorites(self, obj):
        return obj.favorite_recipe.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'measurement_unit')
    list_filter = ('title',)
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'color', 'slug')
    list_editable = ('title', 'color', 'slug')
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    list_filter = ('recipe', 'user')
    search_fields = ('user', )
    empty_value_display = '-пусто-'


admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
