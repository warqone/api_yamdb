from django.core.exceptions import ValidationError

from api.constants import BANNED_USERNAMES


def validate_username(value):
    if value.lower() in BANNED_USERNAMES:
        raise ValidationError(
            f'Имя пользователя {value} недопустимо.')
