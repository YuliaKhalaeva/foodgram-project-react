from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet,
                    SubscriptionViewSet, SubscriptionListView)

router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path(
        'users/subscriptions/',
        SubscriptionListView.as_view(),
        name='subscriptions'
    ),
    path(
        'users/<int:user_id>/subscribe/',
        SubscriptionViewSet.as_view(),
        name='subscribe'
    ),
    path('', include(router.urls)),
]
