from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'in_favorite',)
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags')
    readonly_fields = ('in_favorite',)
    filter_horizontal = ('tags',)

    def in_favorite(self, obj):
        return obj.in_favorite.all().count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
