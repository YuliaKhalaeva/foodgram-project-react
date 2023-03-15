from rest_framework.exceptions import APIException


class RecipeError(APIException):
    status_code = 400
