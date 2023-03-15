from rest_framework import serializers
from utils.strings import str_to_file


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            _, file = str_to_file(data)
        return super().to_internal_value(file)
