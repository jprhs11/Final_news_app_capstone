from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Article, Publisher, Newsletter

# Register the Custom User using the specialized UserAdmin
class CustomUserAdmin(UserAdmin):
    # Add your custom 'role' field to the admin edit screens
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
        ('Reader Subscriptions', {'fields': ('subscribed_publishers', 'subscribed_journalists')}),
    )
    # Add 'role' to the user creation screen
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Article)
admin.site.register(Publisher)
admin.site.register(Newsletter)
