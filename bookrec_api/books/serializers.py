from rest_framework import serializers
from .models import Book, Review, Like, UserBookRecommendation, Subscription
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer

User = get_user_model()

class BookSerializer(serializers.ModelSerializer):
    added_by = UserSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = '__all__'
        read_only_fields = ('added_by', 'created_at', 'updated_at')

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return sum(review.rating for review in reviews) / reviews.count()
        return None

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = ('user', 'created_at')

class UserBookRecommendationSerializer(serializers.ModelSerializer):
    recommender = UserSerializer(read_only=True)
    recipient = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = UserBookRecommendation
        fields = '__all__'
        read_only_fields = ('recommender', 'created_at')

class SubscriptionSerializer(serializers.ModelSerializer):
    subscriber = UserSerializer(read_only=True)
    target_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ('subscriber', 'created_at')
