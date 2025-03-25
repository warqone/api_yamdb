from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from reviews.models import Category, Comment, Genre, Review, Title
from api import constants

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        max_length=constants.EMAIL_LENGTH)
    username = serializers.CharField(
        required=True,
        max_length=constants.USERNAME_LENGTH,
        validators=[
            RegexValidator(
                regex=constants.USERNAME_VALIDATOR,
                message=(
                    'Имя пользователя может содержать только буквы, цифры и '
                    'символы @/./+/-/_'),
                code='invalid_username'
            )
        ]
    )

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if username in constants.BANNED_USERNAMES:
            raise serializers.ValidationError(
                f'Использовать имя {username} в качестве username запрещено.'
            )
        if email:
            try:
                user = User.objects.get(email=email)
                if user.username != username:
                    raise serializers.ValidationError(
                        {'email': 'Пользователь с таким email уже существует.'}
                    )
            except User.DoesNotExist:
                pass
        if username:
            try:
                user = User.objects.get(username=username)
                if user.email != email:
                    raise serializers.ValidationError(
                        {'username':
                         f'Пользователь {username} уже существует.'}
                    )
            except User.DoesNotExist:
                pass

        return data

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(
            email=validated_data['email'],
            username=validated_data['username']
        )
        return user, _


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=constants.USERNAME_LENGTH)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, attrs):
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {'username': 'Пользователь с таким username не найден.'},
                code='not_found'
            )

        if not user.is_confirmation_code_valid(confirmation_code):
            raise serializers.ValidationError(
                'Неверный код подтверждения.'
            )
        attrs['user'] = user
        return attrs

    def get_token(self, user):
        return TokenObtainPairSerializer.get_token(user)


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['name', 'slug']
        model = Genre


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['name', 'slug']
        model = Category


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ['id', 'text', 'author', 'score', 'pub_date']
        model = Review

    def validate(self, attrs):
        user = self.context['request'].user
        method = self.context['request'].method
        title_id = self.context['view'].kwargs.get('title_id')
        get_object_or_404(Title, id=title_id)
        if method == 'POST':
            if Review.objects.filter(author=user).exists():
                raise serializers.ValidationError(
                    "Разрешется оставить только один отзыв к произведению"
                )
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ['id', 'text', 'author', 'pub_date']
        model = Comment

    def validate(self, attrs):
        review_id = self.context['view'].kwargs.get('review_id')
        get_object_or_404(Review, id=review_id)
        return attrs


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )

    class Meta:
        fields = [
            'id', 'name', 'year', 'rating', 'genre', 'category', 'description'
        ]
        model = Title

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['category'] = CategorySerializer(instance.category).data
        data['genre'] = GenreSerializer(instance.genre.all(), many=True).data
        return data
