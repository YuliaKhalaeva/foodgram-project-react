import operator
from functools import reduce

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.filters import IngredientTypeFilter
from api.v1.permissions import IsAuthorOrReadOnly
from api.v1.recipes.serializers import (CustomUserSubscribeSerializer,
                                        IngredientTypeSerializer,
                                        RecipeSerializer, TagSerializer)
from recipes.models import IngredientType, Recipe, Subscribe, Tag
from utils.calc import is_subscribed
from utils.fav_shop_cart import favorite_shopping_cart

User = get_user_model()

messages = {'unauthorized': 'User is not authorized',
            'cant_subscribe_yourself': 'You couldnt be subscribe to yourself',
            'subscribed_already': 'You have alredy subscribed',
            'no_subscribe': 'You do not subsribe to this user',
            'cant_unsubscribe_yourself': 'You couldnt unsiscribe yourself',
            'in_cart_already': 'This recipe is already in cart',
            'not_in_cart': 'This recipe is not in cart'}


def get_error_context(message):
    return {'errors': message}


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
        return favorite_shopping_cart(request, Recipe.favorited_by, recipe)

    @action(detail=True, url_path='shopping_cart',
            methods=['POST', 'DELETE'])
    def shopping_cart(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        return favorite_shopping_cart(request, Recipe.cart_of, recipe)


class SubscriptionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CustomUserSubscribeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        current_user = self.request.user
        return User.objects.filter(subscribers__user=current_user)

    @action(detail=True)
    def subscribe(self, request, id):
        author = get_object_or_404(User, pk=id)
        current_user = self.request.user
        if current_user == author:
            return Response(
                get_error_context(messages['cant_subscribe_yourself']),
                status=status.HTTP_400_BAD_REQUEST)
        if is_subscribed(current_user, author):
            return Response(
                get_error_context(messages['subscribed_already']),
                status=status.HTTP_400_BAD_REQUEST)
        Subscribe.objects.create(user=current_user, author=author)
        serializer = self.get_serializer(author)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True)
    def unsubscribe(self, request, id):
        author = get_object_or_404(User, pk=id)
        current_user = self.request.user
        if current_user == author:
            return Response(
                get_error_context(messages['cant_unsubscribe_yourself']),
                status=status.HTTP_400_BAD_REQUEST)
        if not is_subscribed(current_user, author):
            return Response(
                get_error_context(messages['no_subscribe']),
                status=status.HTTP_400_BAD_REQUEST)
        Subscribe.objects.filter(user=current_user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
