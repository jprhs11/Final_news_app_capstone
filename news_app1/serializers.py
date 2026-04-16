# news_app1/serializers.py
from rest_framework import serializers
from .models import User, Article, Publisher, Newsletter


class UserSerializer(serializers.ModelSerializer):
    """
    Handles serialization for the Custom User model.
    Includes role-specific subscription fields and security constraints.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "subscribed_publishers",
            "subscribed_journalists",
        ]
        # Security: Password must be write-only to prevent leakage in
        # GET responses
        extra_kwargs = {"password": {"write_only": True}}


class PublisherSerializer(serializers.ModelSerializer):
    """
    Basic serializer for the Publisher model to handle entity metadata.
    """

    class Meta:
        model = Publisher
        fields = "__all__"


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Article model.
    Includes human-readable names and hyperlinked navigation for the DRF UI.
    """

    # Readable string representation of foreign keys using dotted notation
    author_name = serializers.ReadOnlyField(source="author.username")
    publisher_name = serializers.ReadOnlyField(source="publisher.name")

    # Requirement: Identity URL to make entries clickable in the Browsable API.
    # This allows direct navigation to the Detail View to access the
    # DELETE button.
    url = serializers.HyperlinkedIdentityField(view_name="article-detail")

    class Meta:
        model = Article
        fields = [
            "id",
            "url",
            "title",
            "content",
            "author",
            "author_name",
            "publisher",
            "publisher_name",
            "approved",
            "created_at",
        ]
        # These fields are managed by backend logic (views/models),
        # not user input
        read_only_fields = ["author", "approved", "created_at"]


class NewsletterSerializer(serializers.ModelSerializer):
    """
    Handles Newsletter data with nested Article details.
    Manages Many-to-Many relationships via write-only ID fields.
    """

    # Nested Serializer: Provides full article data for GET requests
    articles = ArticleSerializer(many=True, read_only=True)

    # Input Handler: Allows users to pass a list of primary keys (IDs)
    # when posting
    article_ids = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all(),
        many=True,
        write_only=True,
        source="articles",
    )

    class Meta:
        model = Newsletter
        fields = [
            "id",
            "title",
            "description",
            "author",
            "articles",
            "article_ids",
            "created_at",
        ]
        # Author and Timestamp are immutable via the API
        read_only_fields = ["author", "created_at"]
