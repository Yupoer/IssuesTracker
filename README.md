# IssuesTracker

A RESTful issue tracking API built with **Django 6.0** and **Django REST Framework**, featuring JWT authentication, role-based permissions, and Docker support.

---

## Table of Contents

- [Introduction](#-introduction)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
  - [Local Development](#local-development)
  - [Docker](#docker)
- [API Endpoints](#-api-endpoints)
- [Running Tests](#-running-tests)
- [License](#-license)

---

## Introduction

**IssuesTracker** is a backend API service for tracking issues/bugs in software projects. It provides a complete CRUD interface for issue management, with support for user authentication, issue assignment, tagging, commenting, and filtering.

The API is designed with security in mind — only the reporter of an issue can modify or delete it, while other authenticated users have read-only access.

---

## Features

- **JWT Authentication** — Secure token-based auth via `simplejwt`
- **CRUD Operations** — Full create, read, update, delete for issues
- **Role-Based Permissions** — Only reporters can modify/delete their own issues
- **Filtering** — Filter issues by `status`, `priority`, `assignee`, `reporter`
- **Pagination** — Built-in page number pagination (10 items/page)
- **Rate Limiting** — Throttle protection for both anonymous and authenticated users
- **Custom User Model** — Extensible `AbstractUser` for future enhancements
- **Tagging System** — Categorize issues with color-coded tags
- **Comments** — Users can comment on issues
- **Docker Ready** — One-command deployment with Docker Compose

---

## Tech Stack

| Category       | Technology                          |
|----------------|-------------------------------------|
| Framework      | Django 6.0.3                        |
| API            | Django REST Framework 3.16          |
| Authentication | SimpleJWT 5.5                       |
| Filtering      | django-filter 25.2                  |
| Database       | SQLite (dev) / PostgreSQL (docker)  |
| Testing        | pytest + pytest-django              |
| Server         | Gunicorn                            |
| Container      | Docker + Docker Compose             |

---

## Project Structure

```
IssuesTracker/
├── config/
│   ├── settings.py          # Django settings
│   ├── urls.py              # Root URL configuration
│   └── wsgi.py              # WSGI entry point
├── issues/
│   ├── models.py            # User, Issue, Tag, Comment models
│   ├── views.py             # IssueViewSet
│   ├── serializers.py       # IssueSerializer
│   ├── permissions.py       # IsReporterOrReadOnly permission
│   └── tests.py             # pytest test cases
├── Dockerfile               # Container image definition
├── docker-compose.yml       # Multi-service orchestration
├── requirements.txt         # Python dependencies
├── pytest.ini               # pytest configuration
├── manage.py                # Django management script
└── README.md
```

---

## Quick Start

### Prerequisites

- Python 3.14+
- pip

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/your-username/IssuesTracker.git
cd IssuesTracker

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run database migrations
python manage.py migrate

# 5. Create a superuser (optional)
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`.

### Docker

```bash
# Build and start all services
docker compose up --build

# Run in detached mode
docker compose up --build -d
```

The API will be available at `http://localhost:8000/api/`.

---

## API Endpoints

### Authentication

| Method | Endpoint             | Description              |
|--------|----------------------|--------------------------|
| POST   | `/api/token/`        | Obtain JWT token pair     |
| POST   | `/api/token/refresh/` | Refresh access token     |

### Issues

| Method | Endpoint              | Description           |
|--------|-----------------------|-----------------------|
| GET    | `/api/issues/`        | List all issues       |
| POST   | `/api/issues/`        | Create a new issue    |
| GET    | `/api/issues/{id}/`   | Retrieve an issue     |
| PUT    | `/api/issues/{id}/`   | Update an issue       |
| PATCH  | `/api/issues/{id}/`   | Partial update        |
| DELETE | `/api/issues/{id}/`   | Delete an issue       |

### Query Parameters

Filter issues using query parameters:

```
GET /api/issues/?status=OPEN&priority=HIGH&assignee=1
```

| Parameter  | Values                                      |
|------------|---------------------------------------------|
| `status`   | `OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED` |
| `priority` | `LOW`, `MEDIUM`, `HIGH`                     |
| `assignee` | User ID                                     |
| `reporter` | User ID                                     |

---

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v
```

### Test Cases

- **Permission Test** — Verifies that a user cannot delete another user's issue (expects `403 Forbidden`)
- **Read-Only Fields Protection** — Ensures `reporter` and `created_at` cannot be forged via API payload

---

## License

This project is licensed under the [MIT License](LICENSE).
