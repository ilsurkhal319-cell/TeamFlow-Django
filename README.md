# TeamFlow

TeamFlow is a Trello-style task management application for teams. Users can create workspaces, boards, columns and tasks, then track work through a simple visual interface.

The project is a learning pet project focused on Django backend development and production-like local tooling.

## Stack

- Python 3.13
- Django 5 and Django REST Framework
- PostgreSQL 17
- Docker and Docker Compose
- HTML, Tailwind CSS and JavaScript
- Django TestCase and GitHub Actions

## Features

- User registration, login and editable profiles
- Workspaces, boards, columns and tasks
- Task priorities, due dates, labels, comments and notifications
- Favorites and archived boards
- Drag-and-drop task movement between columns
- Search tasks on a board
- JSON and DRF API endpoints with authentication and object-level access checks
- Recent activity panel on the dashboard

## Quick Start With Docker

1. Copy the environment template:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Start the application and PostgreSQL:

   ```powershell
   docker compose up --build
   ```

3. Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

Migrations run automatically when the `web` container starts. To create an administrator:

```powershell
docker compose exec web python manage.py createsuperuser
```

To stop the containers while preserving the database volume:

```powershell
docker compose down
```

## Local Development

Create and activate a virtual environment, install dependencies and create `.env` from `.env.example`.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd tm
python manage.py migrate
python manage.py runserver
```

For local execution set `DB_HOST=127.0.0.1` in `.env`. Docker Compose overrides it with `db` inside the `web` container.

## Tests

Run the test suite locally:

```powershell
cd tm
python manage.py test flow
```

Or run it inside the application container:

```powershell
docker compose exec web python manage.py test flow
```

GitHub Actions runs the Django test suite against PostgreSQL for each push and pull request.

## Project Structure

```text
TeamFlow/
├── tm/
│   ├── flow/          # workspaces, boards, tasks and API
│   ├── users/         # custom user model and authentication
│   ├── static/        # JavaScript and styles
│   └── manage.py
├── Dockerfile
├── compose.yaml
├── .env.example
└── requirements.txt
```

