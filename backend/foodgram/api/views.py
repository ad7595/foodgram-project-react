from django.http import FileResponse
from rest_framework import permissions, status
from .filters import IngredientSearchFilter, RecipeFilter
from .permissions import IsOwnerOrReadOnly, IsAdmin
from .pagination import CustomPagination
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .serializers import (IngredientSerializer, CreateRecipeSerializer,
                          RecipeSerializer, RecipeShortSerializer,
                          TagSerializer, FavoriteSerializer,
                          ShoppingCartSerializer)
from recipes.models import (Ingredient, Tag,
                            Recipe, ShoppingCart, RecipeIngredient)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrReadOnly, IsAdmin,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CreateRecipeSerializer
        return RecipeSerializer

    @staticmethod
    def post_del_recipe(request, pk, serializers):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, request, pk, database):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if not database.objects.filter(
                    user=self.request.user,
                    recipe=recipe).exists():
                database.objects.create(
                    user=self.request.user,
                    recipe=recipe)
                serializer = RecipeShortSerializer(recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            text = 'err: Рецепт находится в списке.'
            return Response(text, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            if database.objects.filter(
                    user=self.request.user,
                    recipe=recipe).exists():
                database.objects.filter(
                    user=self.request.user,
                    recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            text = 'err: Рецепта нет в списке.'
            return Response(text, status=status.HTTP_400_BAD_REQUEST)

        else:
            text = 'err: Неверный метод запроса.'
            return Response(text, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        return self.post_del_recipe(request, pk, FavoriteSerializer)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.post_del_recipe(request, pk, ShoppingCartSerializer)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        purchases = ShoppingCart.objects.filter(user=user)
        file = 'shopping-list.txt'
        with open(file, 'w') as f:
            shop_cart = dict()
            for purchase in purchases:
                ingredients = RecipeIngredient.objects.filter(
                    recipe=purchase.recipe.id
                )
                for r in ingredients:
                    i = Ingredient.objects.get(pk=r.ingredient.id)
                    point_name = f'{i.name} ({i.measurement_unit})'
                    if point_name in shop_cart.keys():
                        shop_cart[point_name] += r.amount
                    else:
                        shop_cart[point_name] = r.amount

            for name, amount in shop_cart.items():
                f.write(f'* {name} - {amount}\n')

        return FileResponse(open(file, 'rb'), as_attachment=True)
