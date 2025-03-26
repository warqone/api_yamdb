import csv
from django.core.management.base import BaseCommand
from django.db import transaction

from reviews.models import Category, Genre, Title, Review, Comment
from users.models import User


class Command(BaseCommand):
    help = 'Импорт данных из CSV-файлов в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--categories',
            type=str,
            help='Путь к CSV-файлу с категориями'
        )
        parser.add_argument(
            '--genres',
            type=str,
            help='Путь к CSV-файлу с жанрами'
        )
        parser.add_argument(
            '--titles',
            type=str,
            help='Путь к CSV-файлу с произведениями'
        )
        parser.add_argument(
            '--users',
            type=str,
            help='Путь к CSV-файлу с пользователями'
        )
        parser.add_argument(
            '--reviews',
            type=str,
            help='Путь к CSV-файлу с отзывами'
        )
        parser.add_argument(
            '--comments',
            type=str,
            help='Путь к CSV-файлу с комментариями'
        )
        parser.add_argument(
            '--genre_title',
            type=str,
            help='Путь к CSV-файлу со связями произведений и жанров'
        )

    def handle_category(self, row):
        Category.objects.get_or_create(
            id=row['id'],
            name=row['name'],
            slug=row['slug']
        )

    def handle_genre(self, row):
        Genre.objects.get_or_create(
            id=row['id'],
            name=row['name'],
            slug=row['slug']
        )

    def handle_title(self, row):
        category = Category.objects.get(id=row['category'])
        title, _ = Title.objects.get_or_create(
            id=row['id'],
            name=row['name'],
            year=row['year'],
            category=category,
            description=row.get('description', '')
        )

    def handle_user(self, row):
        User.objects.get_or_create(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            role=row.get('role', 'user'),
            bio=row.get('bio', ''),
            first_name=row.get('first_name', ''),
            last_name=row.get('last_name', '')
        )

    def handle_review(self, row):
        title = Title.objects.get(id=row['title_id'])
        author = User.objects.get(id=row['author'])
        Review.objects.get_or_create(
            id=row['id'],
            title=title,
            text=row['text'],
            author=author,
            score=row['score'],
            pub_date=row['pub_date']
        )

    def handle_comment(self, row):
        review = Review.objects.get(id=row['review_id'])
        author = User.objects.get(id=row['author'])
        Comment.objects.get_or_create(
            id=row['id'],
            review=review,
            text=row['text'],
            author=author,
            pub_date=row['pub_date']
        )

    def handle_genre_title(self, row):
        title = Title.objects.get(id=row['title_id'])
        genre = Genre.objects.get(id=row['genre_id'])
        title.genre.add(genre)

    @transaction.atomic
    def handle(self, *args, **options):
        handlers = {
            'categories': (
                self.handle_category, ['id', 'name', 'slug']),
            'genres': (self.handle_genre, ['id', 'name', 'slug']),
            'titles': (
                self.handle_title, ['id', 'name', 'year', 
                                    'category', 'genre', 'description']),
            'users': (
                self.handle_user, ['id', 'username', 'email',
                                   'role', 'bio', 'first_name', 'last_name']),
            'reviews': (
                self.handle_review, ['id', 'title_id', 'text',
                                     'author', 'score', 'pub_date']),
            'comments': (
                self.handle_comment, ['id', 'review_id', 'text',
                                      'author', 'pub_date']),
            'genre_title': (
                self.handle_genre_title, ['id', 'title_id', 'genre_id']),
        }

        for model, (handler, fields) in handlers.items():
            if file_path := options.get(model):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            try:
                                handler(row)
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(
                                    f'Ошибка в строке {reader.line_num}: {e}'
                                ))
                    self.stdout.write(self.style.SUCCESS(
                        f'Данные для {model} успешно импортированы!'
                    ))
                except FileNotFoundError:
                    self.stdout.write(self.style.ERROR(
                        f'Файл {file_path} не найден!'
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Ошибка при обработке {model}: {e}'
                    ))
