from django.contrib.auth import get_user_model
from rest_framework import filters, mixins, pagination, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .permissions import IsAdminOnly
from .serializers import UserSerializer

User = get_user_model()


class UserViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, IsAdminOnly,)
    pagination_class = pagination.LimitOffsetPagination
    queryset = User.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^username',)
    serializer_class = UserSerializer

    @action(detail=False, methods=['get', 'patch'], url_path='me',
            permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get', 'patch', 'delete'],
            url_path='(?P<username>[^/.]+)')
    def username(self, request, username=None):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Пользователь не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
