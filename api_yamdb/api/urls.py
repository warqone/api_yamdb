from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet
from .views import SignUpView, TokenView

router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='user')
auth_urls = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('token/', TokenView.as_view(), name='token'),
]

urlpatterns = [
    path('v1/auth/', include(auth_urls)),
    path('v1/', include(router_v1.urls)),
]
