from random import randint

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters import rest_framework
from rest_framework import (filters, mixins, status, viewsets, pagination,
                            permissions, response, views)

from reviews.models import Category, Comment, Genre, Review, Title
from users.permissions import AdminPermission, UserPermission
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignUpSerializer,
                          TitleSerializer, TokenSerializer)
from .utils import get_avg_score

User = get_user_model()


class CreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass


class SignUpView(views.APIView):
    permission_classes = (permissions.AllowAny,)

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

            return response.Response(
                {"email": email, "username": user.username},
                status=status.HTTP_200_OK
            )
        return response.Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class TokenView(views.APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
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
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)
    permission_classes = [AdminPermission, ]
    lookup_field = 'slug'


class GenreViewSet(CreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)
    permission_classes = [AdminPermission, ]
    lookup_field = 'slug'


class TitleFilter(rest_framework.FilterSet):
    genre = rest_framework.CharFilter(field_name='genre__slug',
                                      lookup_expr='exact')
    category = rest_framework.CharFilter(field_name='category__slug',
                                         lookup_expr='exact')

    class Meta:
        model = Title
        fields = ['name', 'year', 'genre', 'category']


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (rest_framework.DjangoFilterBackend,
                       filters.SearchFilter)
    filterset_class = TitleFilter
    search_fields = ('name', 'description')
    permission_classes = [AdminPermission, ]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [UserPermission, ]
    pagination_class = pagination.LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def perform_create(self, serializer):
        title_id = self.kwargs['title_id']
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(
            author=self.request.user,
            title_id=title_id
        )
        get_avg_score(title)

    def perform_update(self, serializer):
        review = serializer.save()
        title = review.title
        get_avg_score(title)

    def perform_update(self, serializer):
        review = serializer.save()
        title = review.title
        get_avg_score(title)

    def get_queryset(self):
        return Review.objects.filter(title=self.kwargs.get('title_id'))


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [UserPermission, ]
    serializer_class = CommentSerializer
    pagination_class = pagination.LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review_id=self.kwargs['review_id']
        )

    def get_queryset(self):
        return Comment.objects.filter(
            review=self.kwargs.get('review_id')
        )
