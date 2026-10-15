# Bob Todo App

A simple full-stack todo application built with a **Python Flask** backend and a **vanilla JavaScript** frontend. Created as part of Lab 1.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12 + Flask 3 |
| Database | SQLite via Flask-SQLAlchemy |
| Frontend | HTML5 + CSS3 + vanilla JavaScript |
| CORS | Flask-CORS |

---

## Project Structure

```
todo-app/
├── backend/
│   ├── app.py           # Flask app & REST API routes
│   ├── models.py        # SQLAlchemy Todo model
│   ├── database.py      # DB initialisation
│   ├── test_app.py      # Unit tests (pytest)
│   └── requirements.txt # Python dependencies
└── frontend/
    ├── index.html       # Single-page UI
    ├── styles.css       # Responsive styling
    └── app.js           # Fetch-based API client
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/todos` | List all todos |
| `POST` | `/api/todos` | Create a new todo |
| `PUT` | `/api/todos/<id>` | Update title, description, or completed |
| `DELETE` | `/api/todos/<id>` | Delete a todo |

### Todo model fields

| Field | Type | Notes |
|---|---|---|
| `id` | integer | Auto-increment primary key |
| `title` | string | Required |
| `description` | string | Optional |
| `completed` | boolean | Default `false` |
| `created_at` | datetime | Auto-set on creation |

---

## Getting Started

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The API will be available at `http://127.0.0.1:5000`.

### 2. Frontend

Open `frontend/index.html` directly in your browser, or serve it locally:

```bash
cd frontend
python3 -m http.server 3000
# then open http://localhost:3000
```

---

## Running Tests

```bash
cd backend
source venv/bin/activate
pip install pytest pytest-cov
pytest test_app.py -v --cov=. --cov-report=term-missing
```

---

## Features

- Add todos with a title and optional description
- Mark todos as complete / incomplete
- Delete todos
- Filter by All / Active / Completed
- Responsive design — works on mobile and desktop
- Data persists in a local SQLite file (`todos.db`)
