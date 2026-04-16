from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending AbstractUser to include role-based access.

    Roles include Reader, Journalist, and Editor. This model handles
    subscription relationships for Readers and automatically manages
    Django Group assignments based on the chosen role.
    """

    ROLE_CHOICES = (
        ("Reader", "Reader"),
        ("Journalist", "Journalist"),
        ("Editor", "Editor"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Reader-specific subscription fields
    subscribed_publishers = models.ManyToManyField(
        "Publisher", blank=True, related_name="reader_subscribers"
    )
    subscribed_journalists = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="journalist_followers",
    )

    def save(self, *args, **kwargs):
        """
        Overrides the save method to handle group assignment and
        field cleanup based on the user's role.
        """
        # Initial save to get Primary Key
        super().save(*args, **kwargs)

        # 1. Group Assignment based on Capitalized Role
        if self.role:
            group, _ = Group.objects.get_or_create(name=self.role)
            self.groups.add(group)

        # 2. "Vice Versa" Requirement: Clean up irrelevant fields
        if self.role in ["Journalist", "Editor"]:
            if self.pk:
                self.subscribed_publishers.clear()
                self.subscribed_journalists.clear()


class Publisher(models.Model):
    """
    Represents a publishing organization.

    Links Editors and Journalists to a specific publication entity.
    """

    name = models.CharField(max_length=255)
    editors = models.ManyToManyField(User, related_name="edited_publications")
    journalists = models.ManyToManyField(
        User, related_name="employer_publications"
    )

    def __str__(self):
        """Returns the string representation of the Publisher name."""
        return self.name


class Article(models.Model):
    """
    Represents a news article submitted by a Journalist.

    Contains content, approval status, and feedback notes from Editors.
    """

    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="articles"
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="published_articles",
    )
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    review_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        """Returns the string representation of the Article title."""
        return self.title


class Newsletter(models.Model):
    """
    A curated collection of approved articles created by a Journalist.

    Requires Editor approval before becoming visible to Readers.
    """

    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_newsletters"
    )
    articles = models.ManyToManyField(
        Article, related_name="included_in_newsletters"
    )
    approved = models.BooleanField(default=False)

    def __str__(self):
        """Returns the string representation of the Newsletter title."""
        return self.title
