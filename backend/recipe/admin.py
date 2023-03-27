from django.contrib import admin

from .models import Tag, Recipe, Ingredient
from .models import IngredientAmount, Favorite, Shopping


admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(IngredientAmount)
admin.site.register(Favorite)
admin.site.register(Shopping)
