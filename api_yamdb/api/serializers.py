from rest_framework import serializers

from reviews.models import Title, Genre, Category


class TitleSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['id', 'name', 'year', 'category']
        model = Title


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['id', 'name', 'slug']
        model = Genre


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['id', 'name', 'slug']
        model = Category
