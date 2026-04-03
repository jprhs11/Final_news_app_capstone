from django.apps import AppConfig

class NewsApp1Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news_app1'  # Make sure this matches your folder name

    def ready(self):
        # This tells Django to look into your signals.py file 
        # as soon as the app is loaded.
        import news_app1.signals 
