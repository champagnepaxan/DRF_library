from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg
from .models import Book, Review, Like, UserBookRecommendation, Subscription
from .serializers import BookSerializer, ReviewSerializer, LikeSerializer, UserBookRecommendationSerializer, SubscriptionSerializer
from users.models import CustomUser
import requests

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.annotate(
        like_count=Count('likes'),
        review_count=Count('reviews'),
        average_rating=Avg('reviews__rating')
    )
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        book = self.get_object()
        like, created = Like.objects.get_or_create(
            book=book,
            user=request.user
        )
        if not created:
            like.delete()
            return Response({'status': 'unliked'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        # Simple recommendation logic based on popular books
        popular_books = Book.objects.annotate(
            like_count=Count('likes'),
            review_count=Count('reviews')
        ).order_by('-like_count', '-review_count')[:10]
        serializer = self.get_serializer(popular_books, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search_external(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Query parameter "q" is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Example integration with Open Library API
        try:
            response = requests.get(
                f'https://openlibrary.org/search.json?q={query}&limit=5'
            )
            response.raise_for_status()
            data = response.json()
            simplified_results = []
            for doc in data.get('docs', [])[:5]:
                simplified_results.append({
                    'title': doc.get('title', ''),
                    'author': ', '.join(doc.get('author_name', ['Unknown'])),
                    'published_date': doc.get('first_publish_year', ''),
                    'isbn': doc.get('isbn', [''])[0] if doc.get('isbn') else '',
                    'cover_id': doc.get('cover_i', ''),
                })
            return Response(simplified_results)
        except requests.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(book_id=self.kwargs.get('book_pk'))

    def perform_create(self, serializer):
        book = get_object_or_404(Book, pk=self.kwargs.get('book_pk'))
        serializer.save(user=self.request.user, book=book)

class UserBookRecommendationViewSet(viewsets.ModelViewSet):
    queryset = UserBookRecommendation.objects.all()
    serializer_class = UserBookRecommendationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(recipient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(recommender=self.request.user)

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(subscriber=self.request.user)

    def perform_create(self, serializer):
        serializer.save(subscriber=self.request.user)
