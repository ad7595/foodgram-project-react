from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from recipes.models import Ingredient, Recipe, Tag
from .pagination import CustomPagination
from .filters import IngredientSearchFilter, RecipeFilter
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (
    IngredientSerializer,
    FavoriteSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)
from recipes.models import Favorite, RecipeIngredient


class TagViewSet(ModelViewSet):
    """Вьюсет тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny, ]


class IngredientViewSet(ModelViewSet):
    """Вьюсет игридиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny, ]
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter
    search_fields = ('name',)


class RecipeViewSet(ModelViewSet):
    """Вьюсет рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly, ]
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @staticmethod
    def add_note(request, pk, current_serializer):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = current_serializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED, data=serializer.data)

    @action(detail=True, methods=['post'])
    def shopping_cart(self, request, pk):
        return self.add_note(
            request, pk, current_serializer=ShoppingCartSerializer
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

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk):
        return self.add_note(
            request, pk, current_serializer=FavoriteSerializer
        )

    @action(detail=True, methods=['delete'])
    def delete_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
