# news_app1/serializers.py
from rest_framework import serializers
from .models import User, Article, Publisher, Newsletter


class UserSerializer(serializers.ModelSerializer):
    """
    Handles serialization for the Custom User model,
    including role-specific subscription fields.
    """
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role',
            'subscribed_publishers', 'subscribed_journalists'
        ]
        # Password should never be returned in a GET request
        extra_kwargs = {'password': {'write_only': True}}


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    # Dotted notation (source) allows showing names instead of just IDs
    author_name = serializers.ReadOnlyField(source='author.username')
    publisher_name = serializers.ReadOnlyField(source='publisher.name')

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'author', 'author_name',
            'publisher', 'publisher_name', 'approved', 'created_at'
        ]
        # Author is set automatically in the view's perform_create
        read_only_fields = ['author', 'approved', 'created_at']


class NewsletterSerializer(serializers.ModelSerializer):
    # many=True is required for the Many-to-Many relationship with Article
    articles = ArticleSerializer(many=True, read_only=True)
    # This allows providing article IDs when creating/updating
    article_ids = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all(),
        many=True,
        write_only=True,
        source='articles'
    )

    class Meta:
        model = Newsletter
        fields = [
            'id', 'title', 'description', 'author',
            'articles', 'article_ids', 'created_at'
        ]
        read_only_fields = ['author', 'created_at']

