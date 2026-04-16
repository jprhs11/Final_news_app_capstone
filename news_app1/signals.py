import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Article


@receiver(post_save, sender=Article)
def handle_article_approval(sender, instance, created, **kwargs):
    """
    Triggers an external API call when an article is approved.
    """
    # Only trigger when an EXISTING article is set to approved=True
    if not created and instance.approved:
        try:
            # Wrapped URL and data to stay under 79 characters
            requests.post(
                "http://localhost:8000/api/approved/",
                data={"id": instance.id},
                timeout=1,
            )
        except Exception as e:
            # This will show in the console if the mock fails
            print(f"Signal executed, but API call failed: {e}")
