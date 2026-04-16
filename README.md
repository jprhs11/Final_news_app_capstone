# News Management & Editorial Portal

## Project Overview
A Django-powered news application designed for modern editorial workflows. This platform features a robust **Role-Based Access Control (RBAC)** system managing the full lifecycle of news—from journalist submission to editorial review and reader publication.

## Key Features & Workflows
*   **Journalist Workflow:** Create, edit, and delete articles/newsletters. *Note: Editing an approved article automatically reverts its status to "Pending" for re-approval.*
*   **Editor Workflow:** Access a dedicated dashboard to Approve, Review, and Edit content. Editors can leave internal review notes for journalists.
*   **Reader Workflow:** Discover authors via directories, manage subscriptions, and view a personalized feed of articles from followed journalists.
*   **Developer API:** A full REST API with JWT authentication for third-party integration or headless operation.

---

## Installation & Setup

### 1. Environment Setup
```bash
# Create a virtual environment
python -m venv .venv

# Activate the environment
# Windows:
.\.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install django djangorestframework djangorestframework-simplejwt mysqlclient

## 2. Database Configuration

Ensure you have a MySQL database named news_db.
Update the DATABASES section in news_app/settings.py with your specific MySQL username and password.
Run the migrations:

bash
python manage.py makemigrations
python manage.py migrate

## 3. Initialize Roles
Crucial: You must run this custom command to create the necessary permission groups (Reader, Journalist, Editor) for the application to function:

bash
python manage.py setup_roles

## 4. Create a Superuser

bash
python manage.py createsuperuser

Running the Application
To start the development server, run:

bash
python manage.py runserver
The application will be available at http://127.0.0.

Usage & Role-Based Functionality
Reader	Default role. Browse the author directory, follow journalists, and view a personalized news feed.
Journalist	Create and manage articles. Access the submission portal. Status reverts to "Pending" if an approved article is edited.
Editor	Access the Editorial Dashboard. Review, edit, and approve/reject submissions. Use "Review Notes" for internal feedback.
Admin	Manage all system users and assign roles (Journalist/Editor) via the /admin panel.