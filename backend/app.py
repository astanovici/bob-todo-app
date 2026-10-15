from flask import Flask, jsonify, request
from flask_cors import CORS
from database import init_db, db
from models import Todo

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todos.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

CORS(app)
init_db(app)


# GET /api/todos — return all todos
@app.route("/api/todos", methods=["GET"])
def get_todos():
    todos = Todo.query.order_by(Todo.created_at.asc()).all()
    return jsonify([t.to_dict() for t in todos]), 200


# POST /api/todos — create a new todo
@app.route("/api/todos", methods=["POST"])
def create_todo():
    data = request.get_json()
    if not data or not data.get("title", "").strip():
        return jsonify({"error": "title is required"}), 400

    todo = Todo(
        title=data["title"].strip(),
        description=data.get("description", "").strip() or None,
    )
    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 201


# PUT /api/todos/<id> — update title, description, or completed
@app.route("/api/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return jsonify({"error": "todo not found"}), 404

    data = request.get_json()
    if "title" in data:
        title = data["title"].strip()
        if not title:
            return jsonify({"error": "title cannot be empty"}), 400
        todo.title = title
    if "description" in data:
        todo.description = data["description"].strip() or None
    if "completed" in data:
        todo.completed = bool(data["completed"])

    db.session.commit()
    return jsonify(todo.to_dict()), 200


# DELETE /api/todos/<id> — delete a todo
@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return jsonify({"error": "todo not found"}), 404

    db.session.delete(todo)
    db.session.commit()
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)
