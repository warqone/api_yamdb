from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SignUpView, TokenView

router_v1 = DefaultRouter()
auth_urls = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('token/', TokenView.as_view(), name='token'),
]

urlpatterns = [
    path('v1/auth/', include(auth_urls)),
]
