from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from reviews.models import Title, Genre, Category, Review, Comment
from .constants import EMAIL_LENGTH, USERNAME_LENGTH

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=EMAIL_LENGTH)
    username = serializers.CharField(
        required=True,
        max_length=USERNAME_LENGTH,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=(
                    'Имя пользователя может содержать только буквы, цифры и '
                    'символы @/./+/-/_'),
                code='invalid_username'
            )
        ]
    )

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            if user.username != self.initial_data['username']:
                raise serializers.ValidationError(
                    'Пользователь с таким email уже существует.'
                )
        except User.DoesNotExist:
            pass
        return value

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено.'
            )
        try:
            user = User.objects.get(username=value)
            if user.email != self.initial_data['email']:
                raise serializers.ValidationError(
                    'Пользователь с таким username уже существует.'
                )
        except User.DoesNotExist:
            pass
        return value

    def create(self, validated_data):
        user, created = User.objects.get_or_create(
            email=validated_data['email'],
            defaults={'username': validated_data['username']}
        )
        return user, created


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=USERNAME_LENGTH)
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
            raise serializers.ValidationError()
        attrs['user'] = user
        return attrs

    def get_token(self, user):
        return TokenObtainPairSerializer.get_token(user)


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
