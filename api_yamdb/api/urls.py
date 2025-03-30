from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, SignUpView, TitleViewSet, TokenView)

router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='user')
router_v1.register(r'categories', CategoryViewSet, basename='categories')
router_v1.register(r'genres', GenreViewSet, basename='genres')
router_v1.register(r'titles', TitleViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>[0-9]+)/reviews',
    ReviewViewSet,
    basename='title-reviews'
)
router_v1.register(
    r'titles/(?P<title_id>[0-9]+)/reviews/(?P<review_id>[0-9]+)/comments',
    CommentViewSet,
    basename='title-review-comments'
)
auth_urls = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('token/', TokenView.as_view(), name='token'),
]

urlpatterns = [
    path('v1/auth/', include(auth_urls)),
    path('v1/', include(router_v1.urls)),
]
