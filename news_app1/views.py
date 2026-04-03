from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Article, Newsletter
from .serializers import ArticleSerializer, NewsletterSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing articles with role-based access.
    """
    serializer_class = ArticleSerializer

    def get_permissions(self):
        """
        Dynamic Permissions based on the user's role string.
        Ensures Editors and Journalists have appropriate access.
        """
        user = self.request.user

        # Superuser/Staff bypass: access is never blocked for admins
        if user.is_authenticated and (user.is_superuser or user.is_staff):
            return [permissions.IsAuthenticated()]

        # 1. CREATE: Strictly Journalists only
        if self.action == 'create':
            if user.is_authenticated and user.role == 'Journalist':
                return [permissions.IsAuthenticated()]
            return [permissions.IsAdminUser()]

        # 2. UPDATE/DELETE: Editors AND Journalists
        if self.action in ['update', 'partial_update', 'destroy']:
            is_staff_role = user.role in ['Editor', 'Journalist']
            if user.is_authenticated and is_staff_role:
                return [permissions.IsAuthenticated()]
            return [permissions.IsAdminUser()]

        # 3. VIEW: All authenticated users
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """
        Filter queryset based on user roles and subscription status.
        """
        user = self.request.user
        if not user.is_authenticated:
            return Article.objects.none()

        # Handle Subscribed feed
        if self.action == 'subscribed':
            return Article.objects.filter(
                models.Q(publisher__in=user.subscribed_publishers.all()) |
                models.Q(author__in=user.subscribed_journalists.all()),
                approved=True
            )

        # Editors, Journalists, and Staff see EVERYTHING
        is_staff_role = user.role in ['Editor', 'Journalist']
        if user.is_superuser or user.is_staff or is_staff_role:
            return Article.objects.all()

        # Readers only see approved content
        return Article.objects.filter(approved=True)

    @action(detail=False, methods=['get'], url_path='subscribed')
    def subscribed(self, request):
        """
        Custom action to return articles from subscribed sources.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        Set the author to the current user during creation.
        """
        is_journalist = self.request.user.role == 'Journalist'
        if is_journalist or self.request.user.is_staff:
            serializer.save(author=self.request.user)
        else:
            raise PermissionDenied("Only journalists can create articles.")

    def perform_update(self, serializer):
        """
        Validate permissions before saving updates.
        """
        user = self.request.user
        is_staff_role = user.role in ['Editor', 'Journalist']
        if user.is_staff or is_staff_role:
            serializer.save()
        else:
            raise PermissionDenied("You do not have permission to edit this.")


class NewsletterViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Newsletter operations.
    """
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer

    def get_permissions(self):
        user = self.request.user

        if user.is_authenticated and (user.is_superuser or user.is_staff):
            return [permissions.IsAuthenticated()]

        if self.action == 'create':
            if user.is_authenticated and user.role == 'Journalist':
                return [permissions.IsAuthenticated()]
            return [permissions.IsAdminUser()]

        if self.action in ['update', 'partial_update', 'destroy']:
            is_staff_role = user.role in ['Editor', 'Journalist']
            if user.is_authenticated and is_staff_role:
                return [permissions.IsAuthenticated()]
            return [permissions.IsAdminUser()]

        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        is_journalist = self.request.user.role == 'Journalist'
        if is_journalist or self.request.user.is_staff:
            serializer.save(author=self.request.user)
        else:
            raise PermissionDenied(
                "Only journalists can create newsletters."
            )

    def perform_update(self, serializer):
        user = self.request.user
        is_staff_role = user.role in ['Editor', 'Journalist']
        if user.is_staff or is_staff_role:
            serializer.save()
        else:
            raise PermissionDenied("You do not have permission to edit this.")


@login_required
def editor_approval_list(request):
    """
    View for Editors to see unapproved articles.
    """
    # Defensive check: ensure only Editors or Admins access the UI
    is_editor = request.user.role == 'Editor'
    if not is_editor and not request.user.is_superuser:
        return HttpResponseForbidden(
            "Only Editors can access the dashboard."
        )

    articles = Article.objects.filter(approved=False)
    return render(
        request,
        'news_app1/dashboard.html',
        {'articles': articles}
    )


@login_required
def approve_article_action(request, article_id):
    """
    View logic to flip the 'approved' switch for a specific article.
    """
    is_editor = request.user.role == 'Editor'
    if not is_editor and not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        article = get_object_or_404(Article, id=article_id)
        article.approved = True
        # This triggers signals (Email & API POST)
        article.save()
    return redirect('editor_dashboard')
