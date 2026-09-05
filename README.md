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
- Board participants with owner-controlled access
- Joining a board with a shareable code
- Task priorities, due dates, labels, comments and notifications
- Favorites and archived boards
- Drag-and-drop task movement between columns
- Search tasks on a board
- JSON and DRF API endpoints with authentication and object-level access checks
- Recent activity panel on the dashboard

## Быстрый запуск через Docker

1. Скопируйте шаблон окружения:

   ```bash
   cp .env.example .env
   ```

2. Запустите приложение и PostgreSQL:

   ```bash
   docker compose up --build
   ```

3. Откройте [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

Миграции применяются автоматически при запуске контейнера `web`. Чтобы создать администратора:

```bash
docker compose exec web python manage.py createsuperuser
```

Остановить контейнеры, сохранив данные PostgreSQL:

```bash
docker compose down
```

## Локальная разработка без Docker

Создайте виртуальное окружение, установите зависимости и скопируйте `.env.example` в `.env`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd tm
python manage.py migrate
python manage.py runserver
```

Для локального запуска укажите `DB_HOST=127.0.0.1` в `.env`. Docker Compose автоматически переопределяет его на `db` внутри контейнера `web`.

## Тесты

Запустите весь набор тестов:

```bash
cd tm
python manage.py test
```

Или внутри контейнера:

```bash
docker compose exec web python manage.py test
```

GitHub Actions запускает тесты Django на PostgreSQL при каждом push и pull request.

## Доступ к доскам

Рабочее пространство принадлежит пользователю. Каждая доска получает уникальный код присоединения. Владелец может передать его пользователю, после чего тот вводит код на дашборде и получает доступ к доске. Участник видит доску и может работать с её задачами, но не может удалять доску или менять её состав.

## Структура проекта

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
