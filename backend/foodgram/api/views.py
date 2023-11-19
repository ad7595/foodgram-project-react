from rest_framework import (status,
                            viewsets,
                            permissions,
                            response)
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from recipes.models import Ingredient, Recipe, Tag
from .pagination import CustomPagination
from .filters import IngredientSearchFilter, RecipeFilter
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (RecipeSerializer,
                          IngredientSerializer,
                          TagSerializer,
                          ShoppingCartSerializer,
                          FavoriteSerializer)
from recipes.models import Favorite, RecipeIngredient


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = permissions.AllowAny


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = permissions.AllowAny
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = IsAuthorOrAdminOrReadOnly
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def create(self, request, pk, serializers):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        Recipe.objects.filter(user=user, recipe=recipe).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def shopping_cart(self, request, pk):
        return self.create(
            request, pk, serializers=ShoppingCartSerializer
        )

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        shopping_list = '\n'.join([
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])
        filename = 'shopping_list'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk):
        return self.create(
            request, pk, serializers=FavoriteSerializer
        )

    @action(detail=True, methods=['delete'])
    def delete_favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
