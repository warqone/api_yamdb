EMAIL_LENGTH = 254
USERNAME_LENGTH = 150
USERNAME_VALIDATOR = r'^[\w.@+-]+\Z'
BANNED_USERNAMES = ['me']

ROLE_NAME_LENGTH = 10
CONFIRMATION_CODE_LENGTH = 128
USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLE_CHOICES = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)

CHARFIELD_MAX_LENGHT = 256
MIN_RATING = 1
MAX_RATING = 10

LIMIT_STRING = 15
