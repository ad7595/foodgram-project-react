from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from djoser.views import UserViewSet

from api.pagination import CustomPagination
from api.serializers import CustomUserSerializer, SubscriptionSerializer

from .models import Subscription

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Вьюсет пользователей."""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination
    permission_classes = (AllowAny, )
    http_method_names = ('get', 'post', 'head', 'delete')

    def create(self, request, *args, **kwargs):
        password = request.data.get('password')
        if len(password) > 150:
            raise ValidationError(
                'Пароль должен быть не более 150 символов.'
            )
        return super().create(request, *args, **kwargs)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = get_object_or_404(User, id=request.user.id)
        serializer = self.get_serializer(user)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = kwargs.get('id')
        author = get_object_or_404(User, id=author_id)

        if request.method == 'POST':
            subscription = Subscription.objects.create(
                user=user, author=author
            )
            serializer = SubscriptionSerializer(
                subscription,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            return Response(
                status=status.HTTP_201_CREATED,
                data=serializer.data
            )

        subscription = get_object_or_404(
            Subscription, user=request.user, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        serializer_class=SubscriptionSerializer
    )
    def subscriptions(self, request):
        queryset = Subscription.objects.filter(user=request.user)
        recipes_limit = request.query_params.get('recipes_limit')
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages,
            many=True,
            context={'request': request, 'recipes_limit': recipes_limit}
        )
        return self.get_paginated_response(serializer.data)
