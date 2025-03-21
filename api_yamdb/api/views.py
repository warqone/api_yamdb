from random import randint

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination


from reviews.models import Category, Genre, Title, Review, Comment
from .serializers import (CategorySerializer, GenreSerializer, TitleSerializer,
                          SignUpSerializer, TokenSerializer, ReviewSerializer,
                          CommentSerializer)

User = get_user_model()


class SignUpView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user, created = serializer.save()
            confirmation_code = str(randint(10000, 99999))
            user.set_confirmation_code(confirmation_code)

            send_mail(
                subject='Код подтверждения API Yamdb',
                message=(
                    f'Здравствуйте, {user.username}!\n'
                    'Если вы получили это письмо по ошибке, пожалуйста, '
                    'проигнорируйте его!\n'
                    f'Ваш код подтверждения: {confirmation_code}'
                ),
                from_email='no_reply@yambd.com',
                recipient_list=[email],
                fail_silently=True,
            )

            return Response(
                {"email": email, "username": user.username},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = serializer.get_token(user)

            return Response(
                {"token": str(token.access_token)},
                status=status.HTTP_200_OK
            )
        errors = serializer.errors
        if 'username' in errors and errors['username'][0].code == 'not_found':
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
