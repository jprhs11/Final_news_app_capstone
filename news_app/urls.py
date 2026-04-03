# news_app/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from news_app1.views import (
    ArticleViewSet,
    NewsletterViewSet,
    editor_approval_list,
    approve_article_action
)

# Router setup
router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'newsletters', NewsletterViewSet, basename='newsletter')

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='editor_dashboard')),
    path('admin/', admin.site.urls),

    # HTML/CSS Dashboard routes
    path(
        'dashboard/',
        editor_approval_list,
        name='editor_dashboard'
    ),
    path(
        'approve/<int:article_id>/',
        approve_article_action,
        name='approve_article'
    ),

    # API Routes
    path('api/', include(router.urls)),
    path(
        'api/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'api/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path('api-auth/', include('rest_framework.urls')),
    path(
        'api/login/',
        TokenObtainPairView.as_view(),
        name='api_login'
    ),
]
