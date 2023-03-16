import operator
from functools import reduce

from django.contrib.auth import get_user_model
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.filters import IngredientTypeFilter
from api.v1.permissions import IsAuthorOrReadOnly
from api.v1.recipes.serializers import (CustomUserSubscribeSerializer,
                                        IngredientTypeSerializer,
                                        RecipeSerializer, TagSerializer,
                                        SubscribeSerializer)
from recipes.models import IngredientType, Recipe, Subscribe, Tag
from utils.fav_shop_cart import favorite_shopping_cart

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientTypeViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    serializer_class = IngredientTypeSerializer
    queryset = IngredientType.objects.all()
    filter_backends = (IngredientTypeFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    http_method_names = ('get', 'post', 'patch', 'delete')
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        q_list = []
        tags_list = self.request.query_params.getlist('tags')
        if tags_list:
            q_list.append(Q(tags__slug__in=tags_list))
        author_id = self.request.query_params.get('author')
        if author_id is not None:
            q_list.append(Q(author__pk=int(author_id)))
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_in_shopping_cart == str(1):
            q_list.append(Q(pk__in=self.request.user.cart.all()))
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited == str(1):
            q_list.append(Q(pk__in=self.request.user.favorited.all()))
        if q_list:
            return Recipe.objects.filter(
                reduce(operator.and_, q_list)).distinct()
        return Recipe.objects.all()

    @action(detail=True, url_path='favorite',
            methods=['POST', 'DELETE'])
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        return favorite_shopping_cart(request, recipe)

    @action(detail=True, url_path='shopping_cart',
            methods=['POST', 'DELETE'])
    def shopping_cart(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        return favorite_shopping_cart(request, recipe)

    @action(detail=False, url_path='download_shopping_cart', methods=['GET'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        recipes = request.user.cart.all()
        ingredients = IngredientType.objects.filter(
            ingredient_amounts__recipe__in=recipes).annotate(
                sum=Sum('ingredient_amounts__amount'))
        text = '\n'.join([f'{p.name}, {p.sum} {p.measurement_unit.name}'
                          for p in ingredients])
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=test.txt'
        return response


class SubscriptionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CustomUserSubscribeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        current_user = self.request.user
        return User.objects.filter(subscribers__user=current_user)

    @action(detail=True, methods=['POST', 'DELETE'], name='subscribe')
    def subscribe(self, request, id):
        author = get_object_or_404(User, pk=id)
        current_user = self.request.user
        if request.method == 'POST':
            data = {}
            data['current_user'] = current_user.id
            data['author'] = author.id
            serializer = SubscribeSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = self.get_serializer(instance=author)
            return Response(serializer.data)
        if request.method == 'DELETE':
            subscribe = get_object_or_404(
                Subscribe,
                user=current_user,
                author=author
            )
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
