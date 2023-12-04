from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import CustomPagination
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет игридиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter
    search_fields = ('name',)


class RecipeViewSet(ModelViewSet):
    """Вьюсет рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    @staticmethod
    def add_recipes(request, id, current_serializer):
        data = {'user': request.user.id, 'recipe': id}
        serializer = current_serializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED, data=serializer.data)

    @staticmethod
    def delete_recipes(request, id, model):
        object = model.objects.filter(
            user=request.user, recipe_id=id
        )
        if object.exists():
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Рецепта нет в списке'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=['post'])
    def shopping_cart(self, request, pk):
        return self.add_recipes(
            request, pk, ShoppingCartSerializer
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_recipes(
            request, pk, ShoppingCart
        )

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user,
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(
            amount=Sum('amount'),
        )

        shopping_list = ''
        pattern_item_info = (
            '* Наименование: {name}, Ед. изм.:{m_unit}, Кол-во: {amount}\n'
        )
        for i in ingredients:
            item_info = pattern_item_info.format(
                name=i['ingredient__name'],
                m_unit=i['ingredient__measurement_unit'],
                amount=i['amount'],
            )
            shopping_list += item_info

        filename = 'shopping_list'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk):
        return self.add_recipes(
            request, pk, FavoriteSerializer
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_recipes(
            request, pk, Favorite
        )
