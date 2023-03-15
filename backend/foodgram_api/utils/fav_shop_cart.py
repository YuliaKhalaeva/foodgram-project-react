from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

from api.v1.recipes.serializers import RecipeShortSerializer
from recipes.models import Recipe


def favorite_shopping_cart(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    current_user = request.user
    if request.method == 'POST':
        if not current_user.favorited.filter(pk=pk).exists():
            current_user.favorited.add(recipe)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(status.HTTP_400_BAD_REQUEST)
    if current_user.favorited.filter(pk=pk).exists():
        current_user.favorited.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status.HTTP_400_BAD_REQUEST)
