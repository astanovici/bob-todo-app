"""
Unit tests for the Todo REST API.

Uses an in-memory SQLite database so no file is created on disk and
every test starts from a clean state.

Run:
    pytest test_app.py -v --cov=. --cov-report=term-missing
"""

import pytest
from flask import Flask
from flask_cors import CORS
from database import db, init_db
from models import Todo


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    """Create a fresh Flask app backed by an in-memory SQLite database."""
    test_app = Flask(__name__)
    test_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    test_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    test_app.config["TESTING"] = True

    CORS(test_app)
    init_db(test_app)

    # Register the same routes as app.py without importing the module-level
    # app object (which would bind to a different db instance).
    from app import get_todos, create_todo, update_todo, delete_todo

    test_app.add_url_rule("/api/todos", view_func=get_todos, methods=["GET"])
    test_app.add_url_rule("/api/todos", view_func=create_todo, methods=["POST"])
    test_app.add_url_rule("/api/todos/<int:todo_id>", view_func=update_todo, methods=["PUT"])
    test_app.add_url_rule("/api/todos/<int:todo_id>", view_func=delete_todo, methods=["DELETE"])

    yield test_app

    with test_app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_todo(app):
    """Insert one todo and return its dict representation."""
    with app.app_context():
        todo = Todo(title="Buy milk", description="2% please")
        db.session.add(todo)
        db.session.commit()
        return todo.to_dict()


# ---------------------------------------------------------------------------
# GET /api/todos
# ---------------------------------------------------------------------------

class TestGetTodos:
    def test_returns_empty_list_when_no_todos(self, client):
        response = client.get("/api/todos")
        assert response.status_code == 200
        assert response.get_json() == []

    def test_returns_all_todos(self, client, sample_todo):
        response = client.get("/api/todos")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "Buy milk"

    def test_todos_ordered_by_created_at_ascending(self, client, app):
        with app.app_context():
            db.session.add(Todo(title="First"))
            db.session.add(Todo(title="Second"))
            db.session.add(Todo(title="Third"))
            db.session.commit()

        response = client.get("/api/todos")
        titles = [t["title"] for t in response.get_json()]
        assert titles == ["First", "Second", "Third"]

    def test_response_contains_all_fields(self, client, sample_todo):
        data = client.get("/api/todos").get_json()
        todo = data[0]
        for field in ("id", "title", "description", "completed", "created_at"):
            assert field in todo

    def test_completed_defaults_to_false(self, client, sample_todo):
        data = client.get("/api/todos").get_json()
        assert data[0]["completed"] is False


# ---------------------------------------------------------------------------
# POST /api/todos
# ---------------------------------------------------------------------------

class TestCreateTodo:
    def test_creates_todo_with_title_only(self, client):
        response = client.post("/api/todos", json={"title": "Walk the dog"})
        assert response.status_code == 201
        data = response.get_json()
        assert data["title"] == "Walk the dog"
        assert data["description"] is None
        assert data["completed"] is False
        assert data["id"] is not None

    def test_creates_todo_with_title_and_description(self, client):
        response = client.post(
            "/api/todos",
            json={"title": "Read book", "description": "Chapter 3"},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["description"] == "Chapter 3"

    def test_strips_whitespace_from_title(self, client):
        response = client.post("/api/todos", json={"title": "  Trimmed  "})
        assert response.status_code == 201
        assert response.get_json()["title"] == "Trimmed"

    def test_empty_description_stored_as_none(self, client):
        response = client.post("/api/todos", json={"title": "Task", "description": "   "})
        assert response.status_code == 201
        assert response.get_json()["description"] is None

    def test_missing_title_returns_400(self, client):
        response = client.post("/api/todos", json={"description": "no title"})
        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_blank_title_returns_400(self, client):
        response = client.post("/api/todos", json={"title": "   "})
        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_empty_body_returns_400(self, client):
        response = client.post("/api/todos", json={})
        assert response.status_code == 400

    def test_no_json_body_returns_400(self, client):
        response = client.post("/api/todos", data="not json", content_type="text/plain")
        assert response.status_code == 400

    def test_created_todo_persists(self, client):
        client.post("/api/todos", json={"title": "Persisted"})
        todos = client.get("/api/todos").get_json()
        assert any(t["title"] == "Persisted" for t in todos)


# ---------------------------------------------------------------------------
# PUT /api/todos/<id>
# ---------------------------------------------------------------------------

class TestUpdateTodo:
    def test_update_title(self, client, sample_todo):
        todo_id = sample_todo["id"]
        response = client.put(f"/api/todos/{todo_id}", json={"title": "Buy oat milk"})
        assert response.status_code == 200
        assert response.get_json()["title"] == "Buy oat milk"

    def test_update_description(self, client, sample_todo):
        todo_id = sample_todo["id"]
        response = client.put(f"/api/todos/{todo_id}", json={"description": "Oat, not soy"})
        assert response.status_code == 200
        assert response.get_json()["description"] == "Oat, not soy"

    def test_toggle_completed_true(self, client, sample_todo):
        todo_id = sample_todo["id"]
        response = client.put(f"/api/todos/{todo_id}", json={"completed": True})
        assert response.status_code == 200
        assert response.get_json()["completed"] is True

    def test_toggle_completed_false(self, client, sample_todo, app):
        with app.app_context():
            todo = db.session.get(Todo, sample_todo["id"])
            todo.completed = True
            db.session.commit()

        response = client.put(f"/api/todos/{sample_todo['id']}", json={"completed": False})
        assert response.status_code == 200
        assert response.get_json()["completed"] is False

    def test_partial_update_preserves_other_fields(self, client, sample_todo):
        todo_id = sample_todo["id"]
        client.put(f"/api/todos/{todo_id}", json={"completed": True})
        data = client.get("/api/todos").get_json()[0]
        assert data["title"] == "Buy milk"       # unchanged
        assert data["description"] == "2% please"  # unchanged
        assert data["completed"] is True

    def test_update_clears_description_when_blank(self, client, sample_todo):
        todo_id = sample_todo["id"]
        response = client.put(f"/api/todos/{todo_id}", json={"description": "  "})
        assert response.status_code == 200
        assert response.get_json()["description"] is None

    def test_blank_title_returns_400(self, client, sample_todo):
        todo_id = sample_todo["id"]
        response = client.put(f"/api/todos/{todo_id}", json={"title": "   "})
        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_nonexistent_id_returns_404(self, client):
        response = client.put("/api/todos/9999", json={"completed": True})
        assert response.status_code == 404
        assert "error" in response.get_json()


# ---------------------------------------------------------------------------
# DELETE /api/todos/<id>
# ---------------------------------------------------------------------------

class TestDeleteTodo:
    def test_delete_existing_todo(self, client, sample_todo):
        todo_id = sample_todo["id"]
        response = client.delete(f"/api/todos/{todo_id}")
        assert response.status_code == 204
        assert response.data == b""

    def test_deleted_todo_no_longer_returned(self, client, sample_todo):
        todo_id = sample_todo["id"]
        client.delete(f"/api/todos/{todo_id}")
        todos = client.get("/api/todos").get_json()
        assert not any(t["id"] == todo_id for t in todos)

    def test_nonexistent_id_returns_404(self, client):
        response = client.delete("/api/todos/9999")
        assert response.status_code == 404
        assert "error" in response.get_json()

    def test_double_delete_returns_404(self, client, sample_todo):
        todo_id = sample_todo["id"]
        client.delete(f"/api/todos/{todo_id}")
        response = client.delete(f"/api/todos/{todo_id}")
        assert response.status_code == 404
