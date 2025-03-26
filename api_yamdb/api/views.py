from random import randint

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters import rest_framework
from rest_framework import (filters, mixins, pagination, permissions, response,
                            status, views, viewsets)
from rest_framework.decorators import action

from api import serializers
from api.filters import TitleFilter
from api.permissions import AdminPermission, IsAdminOnly, UserPermission
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class CreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = [AdminPermission]
    lookup_field = 'slug'


class SignUpView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = serializers.SignUpSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data['email']
            user, _ = serializer.save()
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
                from_email=settings.EMAIL_BASE,
                recipient_list=[email],
                fail_silently=True,
            )

            return response.Response(serializer.validated_data,
                                     status=status.HTTP_200_OK)
        return response.Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class TokenView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = serializers.TokenSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = serializer.get_token(user)

            return response.Response(
                {"token": str(token.access_token)},
                status=status.HTTP_200_OK
            )
        errors = serializer.errors
        if 'username' in errors and errors['username'][0].code == 'not_found':
            return response.Response(status=status.HTTP_404_NOT_FOUND)
        return response.Response(status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(CreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class GenreViewSet(CreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = serializers.TitleSerializer
    filter_backends = (rest_framework.DjangoFilterBackend,
                       filters.SearchFilter)
    filterset_class = TitleFilter
    search_fields = ('name', 'description')
    permission_classes = [AdminPermission,]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        return super().get_queryset().annotate(
            avg_rating=Avg('reviews__score')
        )


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ReviewSerializer
    permission_classes = [UserPermission]
    pagination_class = pagination.LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs['title_id'])

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title = self.get_title()
        return Review.objects.filter(title=title)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [UserPermission]
    serializer_class = serializers.CommentSerializer
    pagination_class = pagination.LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_review(self):
        return get_object_or_404(
            Review,
            id=self.kwargs['review_id'],
            title_id=self.kwargs['title_id']
        )

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review = self.get_review()
        return Comment.objects.filter(review=review)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, IsAdminOnly,)
    pagination_class = pagination.LimitOffsetPagination
    queryset = User.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^username',)
    serializer_class = serializers.UserSerializer
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(detail=False, methods=['get', 'patch'], url_path='me',
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return response.Response(
                serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_200_OK)
