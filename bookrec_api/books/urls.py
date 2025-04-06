from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, ReviewViewSet, UserBookRecommendationViewSet, SubscriptionViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'recommendations', UserBookRecommendationViewSet, basename='recommendation')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')

review_router = DefaultRouter()
review_router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('books/<int:book_pk>/', include(review_router.urls)),
]