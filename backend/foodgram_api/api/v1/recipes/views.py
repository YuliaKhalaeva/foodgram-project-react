from django.contrib.auth import get_user_model
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from api.v1.filters import IngredientFilter, RecipeFilter
from api.v1.recipes.serializers import (CustomUserSubscribeSerializer,
                                        IngredientTypeSerializer,
                                        RecipeSerializer,
                                        RecipeShortSerializer,
                                        RecipeViewSerializer,
                                        TagSerializer, SubscribeSerializer)
from recipes.models import (Favorites, Ingredient, Recipe,
                            ShoppingCart, Subscribe, Tag)


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    serializer_class = IngredientTypeSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action in {'list', 'retrieve'}:
            return RecipeViewSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)

    @staticmethod
    def favorite_shopping_cart(request, pk, model):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = RecipeShortSerializer(recipe, data=request.data)
            serializer.is_valid(raise_exception=True)
            model.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data, status=HTTP_201_CREATED)
        get_object_or_404(
            model, user=request.user, recipe=recipe
        ).delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        return self.favorite_shopping_cart(request, pk, Favorites)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        return self.favorite_shopping_cart(request, pk, ShoppingCart)

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        ingredients = Ingredient.objects.filter(
            recipe__cart_recipes__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(quantity=Sum('quantity'))
        text = '\n'.join([
            f'{ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]}) '
            f'- {ingredient["quantity"]}'
            for ingredient in ingredients
        ])
        filename = 'shopping_list.txt'
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class SubscriptionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSubscribeSerializer
    permission_classes = IsAuthenticated

    def subscribe(self, request, id):
        author = get_object_or_404(User, pk=id)
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                author, data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=request.user, author=author)
            return Response(serializer.data, status=HTTP_201_CREATED)
        get_object_or_404(
            Subscribe, user=request.user, author=author
        ).delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(followed__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
