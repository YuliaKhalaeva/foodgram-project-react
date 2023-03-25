from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField

from api.v1.users.serializers import CustomUserSerializer

from recipes.models import (Favorites, Tag, Ingredient,
                            Recipe, ShoppingCart,
                            Subscribe, IngredientAmount)


from .exeptions import RecipeError
from .fields import Base64ImageField


User = get_user_model()

messages = {'not_less_1': 'Amount can not be less than 1',
            'ingr_no_repeat': 'Ingredients can not repeat',
            'ingr_not_empty': 'Ingredients can not be empty',
            'tags_not_empty': 'Tags can not be empty',
            'cant_subscribe_yourself': 'You couldnt be subscribe to yourself'}


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('__all__')


class IngredientTypeSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = IngredientType
        fields = '__all__'


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.pk', queryset=Ingredient.objects.all())
    name = serializers.PrimaryKeyRelatedField(
        source='ingredient.name', queryset=Ingredient.objects.all(),
        required=False)
    measurement_unit = serializers.PrimaryKeyRelatedField(
        source='ingredient.measurement_unit.name',
        queryset=Ingredient.objects.all(), required=False)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount', 'name', 'measurement_unit')

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(messages['not_less_1'])
        return value


class TagsField(serializers.RelatedField):
    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        serializer = TagSerializer(value)
        return serializer.data


class CustomUserSubscribeSerializer(CustomUserSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes_limit_str = self.context['request'].query_params.get(
            'recipes_limit')
        recipes_limit = (int(recipes_limit_str)
                         if recipes_limit_str is not None else None)
        recipes = obj.recipes.all()[:recipes_limit]
        serializer = RecipeShortSerializer(recipes, many=True)
        return serializer.data


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(
        source='ingredientamount_set.all', many=True)
    author = CustomUserSerializer(
        read_only=True, default=serializers.CurrentUserDefault())
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    tags = TagsField(many=True, queryset=Tag.objects.all())
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'ingredients', 'text', 'cooking_time',
                  'tags', 'author', 'is_favorited', 'is_in_shopping_cart',
                  'image')

    def get_is_favorited(self, obj):
        return self.context['request'].user in obj.favorited_by.all()

    def get_is_in_shopping_cart(self, obj):
        return self.context['request'].user in obj.cart_of.all()

    def validate_ingredients(self, value):
        if not value:
            raise RecipeError(detail=messages['ingr_not_empty'])
        ingredients_list = [v['ingredient']['pk'] for v in value]
        if len(set(ingredients_list)) != len(ingredients_list):
            raise RecipeError(detail=messages['ingr_no_repeat'])
        return value

    def validate_tags(self, value):
        if not value:
            raise RecipeError(detail=messages['tags_not_empty'])
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        author = self.context['request'].user
        ingredients = validated_data.pop('ingredientamount_set').pop('all')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.__make_tags(recipe, tags)
        self.__make_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        new_tags = validated_data.pop('tags', None)
        if new_tags is not None:
            instance.tags.clear()
            self.__make_tags(instance, new_tags)
        if 'ingredientamount_set' in validated_data:
            new_ingredients = validated_data.pop(
                'ingredientamount_set', None).pop('all', None)
            instance.ingredient_types.clear()
            self.__make_ingredients(instance, new_ingredients)
        for attr in validated_data:
            setattr(instance, attr, validated_data[attr])
        instance.save()
        return instance

    def __make_ingredients(self, recipe, ingredients):
        IngredientAmount.objects.bulk_create([IngredientAmount(
            recipe=recipe,
            ingredient=ingredient['ingredient']['pk'],
            amount=ingredient['amount']) for ingredient in ingredients])

    def __make_tags(self, recipe, tags):
        for tag in tags:
            recipe.tags.add(tag)


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Subscribe
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=['user', 'author']
            )
        ]

    def validate_author(self, value):
        if value == self.initial_data['user']:
            raise serializers.ValidationError(
                detail=messages['cant_subscribe_yourself']
            )
        return value


class RecipeViewSerializer(serializers.ModelSerializer):
    tags = TagSerializer(
        many=True,
        read_only=True,
    )
    author = CustomUserSerializer(
        read_only=True,
    )
    ingredients = IngredientTypeSerializer(
        source='recipeingredient_set',
        many=True,
        read_only=True,
    )
    image = Base64ImageField(required=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author',
                  'ingredients', 'name', 'image',
                  'text', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart')

    def is_item_related(self, recipe, model):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return model.objects.filter(user=request.user, recipe=recipe).exists()

    def get_is_favorited(self, recipe):
        return self.is_item_related(recipe, Favorites)

    def get_is_in_shopping_cart(self, recipe):
        return self.is_item_related(recipe, ShoppingCart)
