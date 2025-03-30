from api.constants import BANNED_USERNAMES
from django.core.exceptions import ValidationError


def validate_username(value):
    if value in BANNED_USERNAMES:
        raise ValidationError(
            f'Имя пользователя {value} недопустимо.')
