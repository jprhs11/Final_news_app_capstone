from django.urls import reverse
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from .models import User, Article, Publisher


class NewsApiTests(APITestCase):
    def setUp(self):
        # Patching signals globally in setUp to prevent external API timeouts
        # during object creation
        self.signal_patcher = patch("news_app1.signals.requests.post")
        self.mock_post = self.signal_patcher.start()

        # Setup users
        self.reader = User.objects.create_user(
            username="r1", password="pw", role="Reader"
        )
        self.journalist = User.objects.create_user(
            username="j1", password="pw", role="Journalist"
        )
        self.editor = User.objects.create_user(
            username="e1", password="pw", role="Editor"
        )

        # Assign Journalist to Group
        journalist_group, _ = Group.objects.get_or_create(name="Journalist")
        self.journalist.groups.add(journalist_group)

        self.publisher = Publisher.objects.create(name="Daily Planet")

        # Create an unapproved article
        self.article = Article.objects.create(
            title="Test",
            content="Test",
            author=self.journalist,
            approved=False,
        )

    def tearDown(self):
        self.signal_patcher.stop()

    def test_reader_access_denied_to_create(self):
        """Verify readers cannot create articles."""
        self.client.force_authenticate(user=self.reader)
        response = self.client.post(
            reverse("article-list"), {"title": "X", "content": "X"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_journalist_can_create_article(self):
        """Verify journalists are allowed to create articles."""
        self.client.force_authenticate(user=self.journalist)
        response = self.client.post(
            reverse("article-list"), {"title": "X", "content": "X"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_subscription_filtering(self):
        """Check if readers only see articles from subscribed journalists."""
        self.reader.subscribed_journalists.add(self.journalist)

        # Manually approve for this specific test
        self.article.approved = True
        self.article.save()

        # Use force_login for template views to avoid 302 redirects
        self.client.force_login(self.reader)
        response = self.client.get(reverse("subscribed_feed"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if articles are in context (for templates) or data (for API)
        articles = (
            response.context["articles"]
            if hasattr(response, "context") and "articles" in response.context
            else response.data
        )
        self.assertEqual(len(articles), 1)

    @patch("news_app1.signals.requests.post")
    def test_editor_approval_triggers_external_api(self, mock_post):
        """Verify that approving an article triggers the signal."""
        mock_post.return_value.status_code = 200

        test_article = Article.objects.create(
            title="Signal Test",
            content="Content",
            author=self.journalist,
            approved=False,
        )

        # Manually approve and save the model to trigger post_save signal
        test_article.approved = True
        test_article.save()

        msg = "The signal was not triggered by the model save."
        self.assertTrue(mock_post.called, msg)
