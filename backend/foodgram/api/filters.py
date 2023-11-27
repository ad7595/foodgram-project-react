from django_filters.rest_framework import (FilterSet, AllValuesMultipleFilter,
                                           BooleanFilter, filters)
from recipes.models import Recipe, Ingredient


class IngredientSearchFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    tags = AllValuesMultipleFilter(field_name='tags__slug')
    is_favorite = BooleanFilter(method='get_favorite')
    is_in_shopping_cart = BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorite', 'is_in_shopping_cart',)

    def get_is_favorite(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset
        return queryset.filter(favorites__user=self.request.user)

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset
        return queryset.filter(shopping_cart__user=self.request.user)
