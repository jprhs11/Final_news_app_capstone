📰 News Portal Capstone Project

A full-stack Django web application featuring a robust role-based access control (RBAC) system for journalists, editors, and readers. This project demonstrates advanced Django workflows, containerization with Docker, and automated documentation with Sphinx.
🚀 Key Features

👥 User Roles

Readers: Explore a directory of journalists and publishers, subscribe to favorites, and view a personalized feed of approved articles.

Journalists: Draft and manage articles, curate approved content into newsletters, and track the status of their submissions.

Editors: A unified dashboard to review, edit, and approve/reject both articles and newsletters. Editors can also create publisher profiles directly from the front-end.

🛠 Technical Enhancements

Version Control: Managed via Git with dedicated feature branches (docs, container).

Documentation: Comprehensive technical docs generated via Sphinx using Python docstrings.

Containerization: Fully containerized using Docker for "plug-and-play" deployment.

PEP 8 Compliance: Code follows strict Python styling guidelines for readability and maintainability.

💻 Local Installation (Virtual Environment)

1. Clone the Repository:
   
       git clone

       cd Final_news_app_capstone

2.. Set up the Virtual Environment:
   
      python -m venv .venv

      Windows:
      ..venv\Scripts\activate
      Mac/Linux:
      source .venv/bin/activate

3. Install Dependencies:

       pip install -r requirements.txt

5. Initialize the Database:
   
       python manage.py migrate

6. Create an Admin Account:

       python manage.py createsuperuser

7. Launch the Server:

       python manage.py runserver

Access the site at: http://127.0.0.1:8000

🐳 Deployment with Docker

The application is containerized to ensure it works on any system without manual configuration.

1. Build the Image:
2. 
docker build -t news-app .

3. Run the Container:
4. 
docker run -p 8000:8000 news-app

5. Setup inside Docker:
6. 
In a separate terminal window, initialize the container's database and admin:

docker exec -it 

(docker ps -q) python manage.py createsuperuser

Access: Open http://localhost:8000/ in your browser.

📚 Technical Documentation (Sphinx)

Technical documentation for modules, views, and models is located in the docs/ directory.

To view: Open docs/build/html/index.html in any web browser.

To rebuild:

cd docs

python -m sphinx.cmd.build -b html source build/html

📁 Project Structure

news_app1/: The primary Django application logic.

news_app1/models.py: Database schema for Users, Articles, Publishers, and Newsletters.

news_app1/views.py: Role-based business logic and permission handling.

docs/: Sphinx configuration and generated HTML files.

Dockerfile: Instructions for building the Docker image.

requirements.txt: List of Python packages required for the project.

🛡 Security & Defensive Coding

Used get_object_or_404 to prevent server crashes on missing data.

Implemented login_required decorators and role-based HttpResponseForbidden checks.

Sensitive files (like local databases) are excluded via .gitignore.

💡 Note for Reviewers

The Docker environment is configured to use SQLite by default to ensure portability and instant functionality across different machines without requiring a pre-configured MySQL server.
