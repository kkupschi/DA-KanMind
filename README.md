# KanMind

KanMind is a REST API for a Kanban project management tool, built with Django
and the Django REST Framework. It lets authenticated users create boards, manage
tasks across status columns, assign work to members and reviewers, and discuss
tasks through comments.

## Features

- Token-based authentication with a custom user model (login via email)
- Boards with members, owner and aggregated task counts
- Tasks with status, priority, assignee, reviewer, due date and comments
- Dedicated endpoints for tasks assigned to or reviewed by the current user
- Comments per task
- Object-level permissions (owner / member / creator)

## Tech Stack

- Python 3.12+
- Django 6.0
- Django REST Framework 3.17
- SQLite (default development database)

## Prerequisites

- Python 3.12 or newer installed
- `pip` and `venv` available

## Installation & Setup

1. Clone the repository and enter the project folder:

   ```bash
   git clone https://github.com/kkupschi/DA-KanMind.git
   cd DA-KanMind
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Apply the database migrations:

   ```bash
   python manage.py migrate
   ```

5. (Optional) Create a superuser to access the admin panel:

   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:

   ```bash
   python manage.py runserver
   ```

The API is now available at `http://127.0.0.1:8000/api/` and the admin panel at
`http://127.0.0.1:8000/admin/`.

## Authentication

All endpoints except registration and login require a token. After registering
or logging in you receive a token that must be sent in the request header:

```
Authorization: Token <your-token>
```

## API Endpoints

Base URL: `http://127.0.0.1:8000/api/`

### Authentication

| Method | Endpoint            | Description                          | Auth |
|--------|---------------------|--------------------------------------|------|
| POST   | `/registration/`    | Create a new user, returns a token   | No   |
| POST   | `/login/`           | Log in, returns a token              | No   |
| GET    | `/email-check/`     | Check if an email is registered      | Yes  |

### Boards

| Method | Endpoint              | Description                       | Permission        |
|--------|-----------------------|-----------------------------------|-------------------|
| GET    | `/boards/`            | List boards the user owns/joined  | Authenticated     |
| POST   | `/boards/`            | Create a board                    | Authenticated     |
| GET    | `/boards/{board_id}/` | Board detail with members & tasks | Owner or member   |
| PATCH  | `/boards/{board_id}/` | Update title and members          | Owner or member   |
| DELETE | `/boards/{board_id}/` | Delete a board                    | Owner only        |

### Tasks

| Method | Endpoint                  | Description                         | Permission              |
|--------|---------------------------|-------------------------------------|-------------------------|
| GET    | `/tasks/assigned-to-me/`  | Tasks where user is the assignee    | Authenticated           |
| GET    | `/tasks/reviewing/`       | Tasks where user is the reviewer    | Authenticated           |
| POST   | `/tasks/`                 | Create a task on a board            | Board member            |
| PATCH  | `/tasks/{task_id}/`       | Update a task (board cannot change) | Board member            |
| DELETE | `/tasks/{task_id}/`       | Delete a task                       | Task creator or owner   |

### Comments

| Method | Endpoint                                      | Description           | Permission       |
|--------|-----------------------------------------------|-----------------------|------------------|
| GET    | `/tasks/{task_id}/comments/`                  | List task comments    | Board member     |
| POST   | `/tasks/{task_id}/comments/`                  | Add a comment         | Board member     |
| DELETE | `/tasks/{task_id}/comments/{comment_id}/`     | Delete a comment      | Comment author   |

## Notes & Specifics

- The Django project package is named `core`; the apps are `auth_app` and
  `kanban_app`, each with its own `api/` package.
- The user model is custom: there is no `username`; users log in with their
  `email` and have a `fullname` field.
- Task `status` must be one of `to-do`, `in-progress`, `review`, `done`.
- Task `priority` must be one of `low`, `medium`, `high`.
- A task's `assignee` and `reviewer` must be members of the task's board.
- The board owner is automatically added as a member on creation.
- The SQLite database (`db.sqlite3`) is intentionally excluded from version
  control and is created locally by `python manage.py migrate`.
