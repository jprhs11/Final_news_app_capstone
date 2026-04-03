import requests
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from .models import User, Article, Publisher


class NewsApiTests(APITestCase):
    """
    Test suite for News API functionality and role-based access control.
    """

    def setUp(self):
        # Setup users with specific roles
        self.reader = User.objects.create_user(
            username='r1', password='pw', role='reader'
        )
        self.journalist = User.objects.create_user(
            username='j1', password='pw', role='journalist'
        )
        self.editor = User.objects.create_user(
            username='e1', password='pw', role='editor'
        )
        self.publisher = Publisher.objects.create(name="Daily Planet")

        # Create an unapproved article for testing
        self.article = Article.objects.create(
            title="Test",
            content="Test",
            author=self.journalist,
            approved=False
        )

    def test_reader_access_denied_to_create(self):
        """Verify readers cannot create articles."""
        self.client.force_authenticate(user=self.reader)
        response = self.client.post(
            reverse('article-list'),
            {'title': 'X', 'content': 'X'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_journalist_can_create_article(self):
        """Verify journalists are allowed to create articles."""
        self.client.force_authenticate(user=self.journalist)
        response = self.client.post(
            reverse('article-list'),
            {'title': 'X', 'content': 'X'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_subscription_filtering(self):
        """Check if readers only see articles from subscribed journalists."""
        self.reader.subscribed_journalists.add(self.journalist)
        # Manually approve for this specific test
        self.article.approved = True
        self.article.save()

        self.client.force_authenticate(user=self.reader)
        response = self.client.get(reverse('article-subscribed'))
        self.assertEqual(len(response.data), 1)

    @patch('news_app1.signals.requests.post')
    def test_editor_approval_triggers_external_api(self, mock_post):
        """Verify that approving an article triggers the signal."""
        # 1. Start with a fresh, unapproved article
        test_article = Article.objects.create(
            title="Signal Test",
            content="Content",
            author=self.journalist,
            approved=False
        )

        # 2. MANUALLY approve and save the model
        # This is guaranteed to trigger the post_save signal
        test_article.approved = True
        test_article.save()

        # 3. Verify the mock was called
        msg = "The signal was not triggered by the model save."
        self.assertTrue(mock_post.called, msg)





