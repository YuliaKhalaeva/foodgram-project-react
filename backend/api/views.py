from django.http import HttpResponse
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from reportlab.pdfbase import pdfmetrics
from rest_framework.decorators import action
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.response import Response

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import CustomPageNumberPagination
from recipe.models import (Tag, Ingredient, Recipe, Shopping,
                           IngredientAmount, Favorite)
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeSerializer, RecipeListSerializer,
                          ShoppingSerializer, FavoriteSerializer,ShortRecipeSerializer)
from .permissions import IsAuthorOrReadOnly


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = [IngredientSearchFilter]
    search_fields = ('^name',)


class RecipeView(ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get_serializer_class(self):
        if self.action in {'list', 'retrieve'}:
            return RecipeListSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)

    @staticmethod
    def favorite_shopping_cart(request, pk, model):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = ShortRecipeSerializer(recipe, data=request.data)
            serializer.is_valid(raise_exception=True)
            model.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(
            model, user=request.user, recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        return self.favorite_shopping_cart(request, pk, Favorite)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        return self.favorite_shopping_cart(request, pk, Shopping)

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        ingredients = IngredientAmount.objects.filter(
            recipe__cart_recipes__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        text = '\n'.join([
            f'{ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]}) '
            f'- {ingredient["amount"]}'
            for ingredient in ingredients
        ])
        filename = 'shopping_list.txt'
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
