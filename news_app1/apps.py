from django.apps import AppConfig


def create_default_groups(sender, **kwargs):
    from django.contrib.auth.models import Group

    # This matches your automated tests exactly
    Group.objects.get_or_create(name="Journalist")
    Group.objects.get_or_create(name="Editor")
    Group.objects.get_or_create(name="Reader")


class NewsApp1Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "news_app1"  # Make sure this matches your folder name

    def ready(self):
        # This tells Django to look into your signals.py file
        # as soon as the app is loaded.
        import news_app1.signals
