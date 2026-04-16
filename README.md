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
Clone the Repository:
bash
git clone <your-repository-url>
cd NEWS_APPLICATION
Use code with caution.
Set up the Virtual Environment:
bash
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
Use code with caution.
Install Dependencies:
bash
pip install -r requirements.txt
Use code with caution.
Initialize the Database:
bash
python manage.py migrate
Use code with caution.
Create an Admin Account:
bash
python manage.py createsuperuser
Use code with caution.
Launch the Server:
bash
python manage.py runserver
Use code with caution.
Access the site at: 127.0.0
🐳 Deployment with Docker
The application is containerized to ensure it works on any system without manual configuration.
Build the Image:
bash
docker build -t news-portal-app .
Use code with caution.
Run the Container:
bash
docker run -p 8000:8000 news-portal-app
Use code with caution.
Setup inside Docker:
In a separate terminal window, initialize the container's database:
bash
docker exec -it $(docker ps -q) python manage.py migrate
docker exec -it $(docker ps -q) python manage.py createsuperuser
Use code with caution.
Access: Open http://localhost:8000/ in your browser.
📚 Technical Documentation (Sphinx)
Technical documentation for modules, views, and models is located in the docs/ directory.
To view the documentation, open docs/build/html/index.html in any web browser.
To rebuild the documentation:
bash
cd docs
python -m sphinx.cmd.build -b html source build/html
Use code with caution.
📁 Project Structure
news_app1/: The primary Django application logic.
news_app1/models.py: Database schema for Users, Articles, Publishers, and Newsletters.
news_app1/views.py: Role-based business logic and permission handling.
docs/: Sphinx configuration and generated HTML files.
Dockerfile: Instructions for building the Docker image.
requirements.txt: List of Python packages required for the project.
🛡 Security & Defensive Coding
Used get_object_or_404 to prevent server crashes on missing data.
Implemented login_required decorators and role-based HttpResponseForbidden checks to protect sensitive dashboards.
Secrets (like database passwords) are handled via environment variables or excluded via .gitignore.
💡 Note for Reviewers
The Docker environment is configured to use SQLite by default to ensure portability and instant functionality across different machines without requiring a pre-configured MySQL server.