# news_app/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView as JWTTokenObtain,
    TokenRefreshView as JWTTokenRefresh,
)

from news_app1 import views as app_views


# Router setup
router = DefaultRouter()
router.register(r"articles", app_views.ArticleViewSet, basename="article")
router.register(
    r"newsletters", app_views.NewsletterViewSet, basename="newsletter"
)

urlpatterns = [
    # --- Core & Admin ---
    path("admin/", admin.site.urls),
    path("", app_views.home_landing_page, name="home"),
    path("register/", app_views.register_user, name="register"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # --- Dashboards & Creation ---
    path(
        "dashboard/", app_views.editor_approval_list, name="editor_dashboard"
    ),
    path(
        "my-articles/",
        app_views.journalist_article_list,
        name="journalist_articles",
    ),
    path(
        "create-article/", app_views.create_article_view, name="create_article"
    ),
    path(
        "create-newsletter/",
        app_views.create_newsletter_view,
        name="create_newsletter",
    ),
    path(
        "approve/<int:article_id>/",
        app_views.approve_article_action,
        name="approve_article",
    ),
    # --- Reader Discovery ---
    path(
        "my-feed/", app_views.subscribed_articles_view, name="subscribed_feed"
    ),
    path(
        "journalists/",
        app_views.journalist_directory,
        name="journalist_directory",
    ),
    path(
        "publishers/",
        app_views.publisher_directory,
        name="publisher_directory",
    ),
    path(
        "newsletters/", app_views.newsletter_list_view, name="newsletter_list"
    ),
    path(
        "article/<int:article_id>/",
        app_views.article_detail_view,
        name="article_detail",
    ),
    path(
        "subscribe/<str:target_type>/<int:target_id>/",
        app_views.toggle_subscription,
        name="toggle_subscription",
    ),
    path(
        "publishers/<int:publisher_id>/articles/",
        app_views.publisher_article_list,
        name="publisher_articles",
    ),
    path(
        "journalists/<int:author_id>/articles/",
        app_views.author_article_list,
        name="author_articles",
    ),
    # --- API & Tokens ---
    path("api/", include(router.urls)),
    path("api/approved/", app_views.api_approved_log, name="api_approved"),
    path("api/token/", JWTTokenObtain.as_view(), name="token_obtain_pair"),
    path(
        "api/token/refresh/", JWTTokenRefresh.as_view(), name="token_refresh"
    ),
    path("api/login/", JWTTokenObtain.as_view(), name="api_login"),
    path("api-auth/", include("rest_framework.urls")),
    path(
        "editor/edit/<int:article_id>/",
        app_views.editor_edit_review,
        name="editor_edit_review",
    ),
    path(
        "article/edit/<int:article_id>/",
        app_views.edit_article_view,
        name="edit_article",
    ),
    path(
        "article/delete/<int:article_id>/",
        app_views.delete_article_view,
        name="delete_article",
    ),
    path(
        "newsletter/delete/<int:newsletter_id>/",
        app_views.delete_newsletter_view,
        name="delete_newsletter",
    ),
    path(
        "publishers/create/",
        app_views.create_publisher_view,
        name="create_publisher",
    ),
    path(
        "editor/newsletters/",
        app_views.editor_newsletter_list,
        name="editor_newsletters",
    ),
    path(
        "my-newsletters/",
        app_views.journalist_newsletter_list,
        name="journalist_newsletters",
    ),
    path(
        "newsletters/edit/<int:newsletter_id>/",
        app_views.edit_newsletter_view,
        name="edit_newsletter",
    ),
    path(
        "newsletters/approve/<int:newsletter_id>/",
        app_views.approve_newsletter_action,
        name="approve_newsletter",
    ),
]

handler404 = "news_app1.views.custom_404_view"
