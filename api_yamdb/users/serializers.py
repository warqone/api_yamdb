from api.constants import EMAIL_LENGTH, USERNAME_LENGTH
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from rest_framework import serializers

from .models import ROLE_CHOICES

User = get_user_model()


class UserSerializer(serializers.Serializer):
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
    email = serializers.EmailField(required=True,
                                   max_length=EMAIL_LENGTH)
    first_name = serializers.CharField(required=False,
                                       max_length=USERNAME_LENGTH)
    last_name = serializers.CharField(required=False,
                                      max_length=USERNAME_LENGTH)
    bio = serializers.CharField(required=False)
    role = serializers.ChoiceField(required=False,
                                   choices=ROLE_CHOICES,
                                   default='user')

    class Meta:
        model = User
        fields = '__all__'

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.')
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует.')
        elif value == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено.')
        return value

    def validate_role(self, value):
        if self.context['request'].user.role in ['admin', 'superuser']:
            return value
        else:
            return 'user'

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name',
                                                 instance.first_name)
        instance.last_name = validated_data.get('last_name',
                                                instance.last_name)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.role = validated_data.get('role', instance.role)
        instance.save()
        return instance
