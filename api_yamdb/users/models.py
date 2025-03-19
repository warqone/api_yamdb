from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    role = models.CharField(
        'Роль',
        max_length=10,
        choices=(
            ('user', 'Пользователь'),
            ('moderator', 'Модератор'),
            ('admin', 'Администратор'),
        ),
        default='user',
    )
    bio = models.TextField('Биография', blank=True)
    confirmation_code_hash = models.CharField(
        'Код подтверждения',
        max_length=128,
        blank=True,
        null=True)
    confirmation_code_created_at = models.TextField(
        'Время создания кода подтверждения',
        blank=True,
        null=True)

    def set_confirmation_code(self, code):
        """Устанавливает хешированный код подтверждения и время создания."""
        self.confirmation_code_hash = make_password(code)
        self.confirmation_code_created_at = timezone.now().strftime(
            '%d-%m-%dY %H:%M:%S'
        )
        self.save()

    def is_confirmation_code_valid(self, code):
        """Проверяет, совпадает ли код."""
        return check_password(code, self.confirmation_code_hash)
