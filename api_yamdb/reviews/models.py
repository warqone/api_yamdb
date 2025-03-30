from datetime import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.constants import (CHARFIELD_MAX_LENGHT, LIMIT_STRING, MAX_RATING,
                           MIN_RATING)
from users.models import User


class CategoryGenreBaseModel(models.Model):
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        abstract = True

    def __str__(self) -> str:
        return self.name


class ReviewComment(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        max_length=CHARFIELD_MAX_LENGHT,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('pub_date',)
        abstract = True

    def __str__(self) -> str:
        return self.text[:LIMIT_STRING]


class Category(CategoryGenreBaseModel):
    name = models.CharField(
        verbose_name='Категория',
        max_length=CHARFIELD_MAX_LENGHT,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(CategoryGenreBaseModel):
    name = models.TextField(
        verbose_name='Жанр',
        max_length=CHARFIELD_MAX_LENGHT,
    )

    class Meta:
        ordering = ('name',)
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
        verbose_name='Рейтинг',
        null=True,
        blank=True,
        validators=[
            MinValueValidator(MIN_RATING),
            MaxValueValidator(MAX_RATING)
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
        ordering = ('name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(ReviewComment):
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(MIN_RATING),
            MaxValueValidator(MAX_RATING)
        ]
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_author',
    )

    class Meta:
        default_related_name = 'reviews.review'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review')]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Comment(ReviewComment):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comment_author',
    )

    class Meta:
        default_related_name = 'reviews.comment'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
