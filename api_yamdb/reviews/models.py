from datetime import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.constants import CHARFIELD_MAX_LENGHT
from users.models import User


class BaseModel(models.Model):
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
    )

    class Meta:
        ordering = ('name', )
        abstract = True

    def __str__(self) -> str:
        return self.name


class Category(BaseModel):
    name = models.CharField(
        verbose_name='Категория',
        max_length=CHARFIELD_MAX_LENGHT,
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseModel):
    name = models.TextField(
        verbose_name='Жанр',
        max_length=CHARFIELD_MAX_LENGHT,
    )

    class Meta:
        verbose_name = 'Жанр',
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=CHARFIELD_MAX_LENGHT,
    )
    year = models.SmallIntegerField(
        verbose_name='Год выпуска',
        validators=[
            MaxValueValidator(datetime.now().year),
        ],
    )
    rating = models.PositiveSmallIntegerField(
        verbose_name='Описание',
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )
    description = models.TextField(
        verbose_name='Описание',
        null=True,
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Slug жанра',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Slug категории',
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField(
        verbose_name='Отзыв',
    )
    author = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
    )


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Комментарий к отзыву',
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )
