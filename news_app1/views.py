from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from rest_framework import viewsets, permissions, filters
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import Article, Newsletter, User, Publisher
from .serializers import ArticleSerializer, NewsletterSerializer

from django import forms
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

# --- FORMS ---


class CustomUserCreationForm(UserCreationForm):
    """Signup form with Reader, Journalist, and Editor roles."""

    role = forms.ChoiceField(
        choices=[
            ("Reader", "Reader"),
            ("Journalist", "Journalist"),
            ("Editor", "Editor"),
        ]
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("role",)


class PublisherCreationForm(forms.ModelForm):
    """Form for Editors to create Publishers from the front-end."""

    class Meta:
        model = Publisher
        fields = ["name"]


# --- AUTH & REGISTRATION ---


def register_user(request):
    """Handles signup and logs the user in automatically."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})


# --- EDITOR WORKFLOW ---


@login_required
def editor_approval_list(request):
    """Dashboard for Editors to review all pending submissions."""
    is_ed = request.user.role == "Editor"
    if not is_ed and not request.user.is_superuser:
        return HttpResponseForbidden("Editors only.")

    # Combined dashboard logic for articles and newsletters
    pending_articles = Article.objects.filter(approved=False)
    pending_newsletters = Newsletter.objects.filter(approved=False)

    return render(
        request,
        "news_app1/dashboard.html",
        {"articles": pending_articles, "newsletters": pending_newsletters},
    )


@login_required
def editor_newsletter_list(request):
    """Master list for Editors to manage existing newsletters."""
    is_ed = request.user.role == "Editor"
    if not is_ed and not request.user.is_superuser:
        return HttpResponseForbidden("Editors only.")
    # Show status-sorted list of all newsletters
    news = Newsletter.objects.all().order_by("approved", "-created_at")
    return render(
        request, "news_app1/editor_newsletters.html", {"newsletters": news}
    )


@login_required
def editor_edit_review(request, article_id):
    """Allows Editors to edit content and leave review notes."""
    is_ed = request.user.role == "Editor"
    if not is_ed and not request.user.is_superuser:
        return HttpResponseForbidden("Editors only.")
    art = get_object_or_404(Article, id=article_id)
    if request.method == "POST":
        art.title = request.POST.get("title")
        art.content = request.POST.get("content")
        art.review_notes = request.POST.get("review_notes")
        if "approve" in request.POST:
            art.approved = True
        art.save()
        return redirect("editor_dashboard")
    return render(request, "news_app1/editor_edit.html", {"article": art})


@login_required
def approve_article_action(request, article_id):
    """Quick POST action to approve an article submission."""
    is_ed = request.user.role == "Editor"
    if not is_ed and not request.user.is_superuser:
        return HttpResponseForbidden()
    if request.method == "POST":
        article = get_object_or_404(Article, id=article_id)
        article.approved = True
        article.save()
    return redirect("editor_dashboard")


@login_required
def approve_newsletter_action(request, newsletter_id):
    """Quick POST action to approve a newsletter submission."""
    is_ed = request.user.role == "Editor"
    if not is_ed and not request.user.is_superuser:
        return HttpResponseForbidden()
    if request.method == "POST":
        news = get_object_or_404(Newsletter, id=newsletter_id)
        news.approved = True
        news.save()
    return redirect("editor_dashboard")


@login_required
def create_publisher_view(request):
    """Allows Editors to create publishers without admin panel."""
    is_ed = request.user.role == "Editor"
    if not is_ed and not request.user.is_superuser:
        return HttpResponseForbidden("Editors only.")

    if request.method == "POST":
        form = PublisherCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("publisher_directory")
    else:
        form = PublisherCreationForm()

    return render(request, "news_app1/create_publisher.html", {"form": form})


# --- JOURNALIST WORKFLOW ---


@login_required
def journalist_newsletter_list(request):
    """Dashboard for Journalists to manage their created work."""
    is_jr = request.user.role == "Journalist"
    if not is_jr and not request.user.is_superuser:
        return HttpResponseForbidden("Journalists only.")
    # Journalists only see their own creations
    news = Newsletter.objects.filter(author=request.user)
    return render(
        request,
        "news_app1/journalist_newsletters.html",
        {"newsletters": news.order_by("-created_at")},
    )


@login_required
def create_article_view(request):
    """UI form for Journalists to submit articles."""
    is_jr = request.user.role == "Journalist"
    if not is_jr and not request.user.is_superuser:
        return HttpResponseForbidden("Journalists only.")
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        pub_id = request.POST.get("publisher")
        pub = get_object_or_404(Publisher, id=pub_id) if pub_id else None
        Article.objects.create(
            title=title, content=content, author=request.user, publisher=pub
        )
        return redirect("journalist_articles")
    pubs = Publisher.objects.all()
    return render(
        request, "news_app1/create_article.html", {"publishers": pubs}
    )


@login_required
def edit_article_view(request, article_id):
    """Edits article and resets approval status for re-review."""
    art = get_object_or_404(Article, id=article_id, author=request.user)
    if request.method == "POST":
        art.title = request.POST.get("title")
        art.content = request.POST.get("content")
        # Edits trigger a new review cycle
        art.approved = False
        art.save()
        return redirect("journalist_articles")
    return render(request, "news_app1/edit_article.html", {"article": art})


@login_required
def delete_article_view(request, article_id):
    """Allows Journalists to delete their own articles."""
    art = get_object_or_404(Article, id=article_id, author=request.user)
    if request.method == "POST":
        art.delete()
    return redirect("journalist_articles")


@login_required
def delete_newsletter_view(request, newsletter_id):
    """Allows Journalists (owners) or Editors to delete newsletters."""
    news = get_object_or_404(Newsletter, id=newsletter_id)
    is_ed = request.user.role == "Editor"
    is_owner = news.author == request.user
    if is_ed or is_owner or request.user.is_superuser:
        if request.method == "POST":
            news.delete()
        return redirect("newsletter_list")
    return HttpResponseForbidden()


@login_required
def create_newsletter_view(request):
    """UI form for Journalists to bundle approved articles."""
    is_jr = request.user.role == "Journalist"
    if not is_jr and not request.user.is_superuser:
        return HttpResponseForbidden()
    if request.method == "POST":
        title = request.POST.get("title")
        desc = request.POST.get("description")
        art_ids = request.POST.getlist("articles")
        news = Newsletter.objects.create(
            title=title, description=desc, author=request.user
        )
        news.articles.set(art_ids)
        return redirect("newsletter_list")
    arts = Article.objects.filter(author=request.user, approved=True)
    return render(
        request, "news_app1/create_newsletter.html", {"articles": arts}
    )


@login_required
def edit_newsletter_view(request, newsletter_id):
    """Allows owners or Editors to modify newsletter content."""
    news = get_object_or_404(Newsletter, id=newsletter_id)
    is_ed = request.user.role == "Editor"
    is_owner = news.author == request.user
    if not (is_ed or is_owner or request.user.is_superuser):
        return HttpResponseForbidden()

    if request.method == "POST":
        news.title = request.POST.get("title")
        news.description = request.POST.get("description")
        art_ids = request.POST.getlist("articles")
        news.articles.set(art_ids)
        news.save()
        return redirect("newsletter_list")

    # Editors can pick any approved article; Journalists pick their own
    if is_ed or request.user.is_superuser:
        arts = Article.objects.filter(approved=True)
    else:
        arts = Article.objects.filter(author=request.user, approved=True)

    return render(
        request,
        "news_app1/edit_newsletter.html",
        {"newsletter": news, "articles": arts},
    )


@login_required
def journalist_article_list(request):
    """Lists articles for the logged-in Journalist."""
    is_jr = request.user.role == "Journalist"
    if not is_jr and not request.user.is_superuser:
        return HttpResponseForbidden()
    arts = Article.objects.filter(author=request.user).order_by("-created_at")
    return render(
        request, "news_app1/journalist_articles.html", {"articles": arts}
    )


# --- DISCOVERY & SUBSCRIPTIONS ---


@login_required
def journalist_directory(request):
    """Directory showing all system journalists."""
    journalists = User.objects.filter(role="Journalist")
    return render(
        request,
        "news_app1/journalist_directory.html",
        {
            "journalists": journalists,
            "is_reader": request.user.role == "Reader",
        },
    )


@login_required
def publisher_directory(request):
    """Directory showing all system publishers."""
    pubs = Publisher.objects.all()
    return render(
        request,
        "news_app1/publisher_directory.html",
        {"publishers": pubs, "is_reader": request.user.role == "Reader"},
    )


@login_required
def toggle_subscription(request, target_type, target_id):
    """Toggles follower relationships for Readers."""
    user = request.user
    if user.role != "Reader":
        return HttpResponseForbidden()
    if target_type == "journalist":
        target = get_object_or_404(User, id=target_id)
        rel = user.subscribed_journalists
    else:
        target = get_object_or_404(Publisher, id=target_id)
        rel = user.subscribed_publishers
    if target in rel.all():
        rel.remove(target)
    else:
        rel.add(target)
    return redirect(request.META.get("HTTP_REFERER", "home"))


@login_required
def subscribed_articles_view(request):
    """Feed restricted to articles from followed journalists."""
    u = request.user
    arts = Article.objects.filter(
        author__in=u.subscribed_journalists.all(), approved=True
    ).order_by("-created_at")

    return render(
        request, "news_app1/subscribed_list.html", {"articles": arts}
    )


# --- API ---


class ArticleViewSet(viewsets.ModelViewSet):
    """API for Article operations with role-based filtering."""

    serializer_class = ArticleSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["id", "title"]

    def get_queryset(self):
        u = self.request.user
        if not u.is_authenticated:
            return Article.objects.filter(approved=True)
        if u.role in ["Editor", "Journalist"] or u.is_superuser:
            return Article.objects.all()
        return Article.objects.filter(approved=True)

    def perform_create(self, serializer):
        is_jr = self.request.user.role == "Journalist"
        if is_jr or self.request.user.is_superuser:
            serializer.save(author=self.request.user)
        else:
            raise PermissionDenied()


class NewsletterViewSet(viewsets.ModelViewSet):
    """API for Newsletter operations."""

    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer


# --- HELPERS ---


def home_landing_page(request):
    """Landing page with aggregated unapproved work counts."""
    ctx = {"is_editor": False, "is_journalist": False, "is_reader": False}
    if request.user.is_authenticated:
        role = getattr(request.user, "role", "")
        ctx["is_reader"] = role == "Reader"
        ctx["is_editor"] = role == "Editor" or request.user.is_superuser
        ctx["is_journalist"] = role == "Journalist"
        sub_p = request.user.subscribed_publishers.exists()
        sub_j = request.user.subscribed_journalists.exists()
        ctx["has_subscriptions"] = sub_p or sub_j

        # Aggregate counts for the Editor's dashboard button
        if ctx["is_editor"]:
            art_count = Article.objects.filter(approved=False).count()
            news_count = Newsletter.objects.filter(approved=False).count()
            ctx["unapproved_count"] = art_count + news_count
        elif ctx["is_journalist"]:
            ctx["my_articles_count"] = Article.objects.filter(
                author=request.user
            ).count()

    return render(request, "news_app1/home.html", ctx)


@login_required
def article_detail_view(request, article_id):
    """Single article reader view."""
    art = get_object_or_404(Article, id=article_id)
    return render(request, "news_app1/article_detail.html", {"article": art})


@login_required
def newsletter_list_view(request):
    """Reader view showing only approved newsletters."""
    news = Newsletter.objects.filter(approved=True)
    return render(
        request, "news_app1/newsletter_list.html", {"newsletters": news}
    )


@login_required
def author_article_list(request, author_id):
    """Public profile for system authors."""
    auth = get_object_or_404(User, id=author_id)
    arts = Article.objects.filter(author=auth, approved=True)
    return render(
        request,
        "news_app1/author_articles.html",
        {"author": auth, "articles": arts},
    )


@login_required
def publisher_article_list(request, publisher_id):
    """Public profile for system publishers."""
    pub = get_object_or_404(Publisher, id=publisher_id)
    arts = Article.objects.filter(publisher=pub, approved=True)
    return render(
        request,
        "news_app1/publisher_articles.html",
        {"publisher": pub, "articles": arts},
    )


@api_view(["POST"])
def api_approved_log(request):
    """Approval logging event API."""
    return Response({"message": "Logged"})


def custom_404_view(request, exception):
    """Branded error page."""
    return render(request, "404.html", status=404)
