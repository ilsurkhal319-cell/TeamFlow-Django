# TeamFlow

TeamFlow is a Django web application for managing tasks, boards, and workspaces.
The project is inspired by tools like Trello and was built as a practice project for learning backend development with Django.

## Features

- User registration and login
- Custom user model
- Workspaces
- Boards
- Columns
- Tasks
- Task priorities
- Labels
- Comments
- Notifications
- Favorite boards
- Archived boards
- JSON API endpoints

## Tech Stack

- Python
- Django
- SQLite
- HTML
- CSS
- JavaScript

## Project Structure

```text
TeamFlow/
├── tm/
│   ├── flow/
│   ├── users/
│   ├── tm/
│   ├── static/
│   ├── templates/
│   └── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Go to the Django project folder:

```bash
cd tm
```

Run migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

Open in browser:

```text
http://127.0.0.1:8000/
```

## Apps

### users

Handles authentication and user-related logic:

- registration
- login
- custom user model
- user profile data

### flow

Contains the main application logic:

- workspaces
- boards
- columns
- tasks
- labels
- comments
- notifications
- API endpoints

## Current Status

The project is in development.
The main functionality is implemented, but the project still needs improvements before production use.

## Planned Improvements

- Move secret settings to environment variables
- Add tests
- Improve API security
- Remove unnecessary `csrf_exempt`
- Add Docker support
- Prepare the project for deployment
