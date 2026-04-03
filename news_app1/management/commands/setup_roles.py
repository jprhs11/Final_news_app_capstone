from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from news_app1.models import Article, Newsletter

class Command(BaseCommand):
    help = 'Initializes User Groups and Permissions for the News App'

    def handle(self, *args, **kwargs):
        # 1. Define the Roles and their required permission "codenames"
        roles = {
            'Reader': {
                'models': [Article, Newsletter],
                'actions': ['view'],
            },
            'Editor': {
                'models': [Article, Newsletter],
                'actions': ['view', 'change', 'delete'],
            },
            'Journalist': {
                'models': [Article, Newsletter],
                'actions': ['add', 'view', 'change', 'delete'],
            },
        }

        for role_name, config in roles.items():
            # Create or get the Group
            group, created = Group.objects.get_or_create(name=role_name)
            
            permissions_to_add = []
            for model in config['models']:
                # Get the "content type" for the model (Article or Newsletter)
                content_type = ContentType.objects.get_for_model(model)
                
                for action in config['actions']:
                    # Standard Django codename format: 'view_article', 'add_newsletter', etc.
                    codename = f"{action}_{model._meta.model_name}"
                    try:
                        perm = Permission.objects.get(content_type=content_type, codename=codename)
                        permissions_to_add.append(perm)
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"Permission {codename} not found."))

            # Assign permissions to the group
            group.permissions.set(permissions_to_add)
            
            status = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"Successfully {status} group: {role_name}"))

