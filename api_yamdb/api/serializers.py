from rest_framework import serializers

from reviews.models import Title, Genre, Category, Review, Comment


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


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['id', 'text', 'author', 'score', 'pub_date']
        model = Review


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['id', 'text', 'author', 'pub_date']
        model = Comment
