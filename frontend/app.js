const API_BASE = "http://127.0.0.1:5000/api";

// ── State ──────────────────────────────────────────────────────────────────
let todos = [];          // full list from the server
let activeFilter = "all"; // "all" | "active" | "completed"

// ── DOM references ─────────────────────────────────────────────────────────
const form            = document.getElementById("todo-form");
const titleInput      = document.getElementById("title-input");
const descInput       = document.getElementById("description-input");
const todoList        = document.getElementById("todo-list");
const emptyState      = document.getElementById("empty-state");
const todoFooter      = document.getElementById("todo-footer");
const todoCount       = document.getElementById("todo-count");
const filterButtons   = document.querySelectorAll(".filter-btn");

// ── API helpers ────────────────────────────────────────────────────────────
async function apiRequest(method, path, body = null) {
  const options = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body !== null) options.body = JSON.stringify(body);

  const response = await fetch(`${API_BASE}${path}`, options);

  if (response.status === 204) return null;
  return response.json();
}

// ── Fetch & render ─────────────────────────────────────────────────────────
async function loadTodos() {
  try {
    todos = await apiRequest("GET", "/todos");
    renderTodos();
  } catch {
    console.error("Could not connect to the backend.");
  }
}

function renderTodos() {
  const filtered = filterTodos(todos, activeFilter);

  todoList.innerHTML = "";

  if (filtered.length === 0) {
    emptyState.classList.remove("hidden");
    todoFooter.classList.add("hidden");
  } else {
    emptyState.classList.add("hidden");
    todoFooter.classList.remove("hidden");
    filtered.forEach((todo) => todoList.appendChild(createTodoItem(todo)));
  }

  updateFooterCount();
}

function filterTodos(list, filter) {
  if (filter === "active")    return list.filter((t) => !t.completed);
  if (filter === "completed") return list.filter((t) => t.completed);
  return list;
}

function updateFooterCount() {
  const remaining = todos.filter((t) => !t.completed).length;
  todoCount.textContent = `${remaining} item${remaining !== 1 ? "s" : ""} left`;
}

// ── Build a <li> for one todo ──────────────────────────────────────────────
function createTodoItem(todo) {
  const li = document.createElement("li");
  li.className = `todo-item${todo.completed ? " completed" : ""}`;
  li.dataset.id = todo.id;

  // Checkbox
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.className = "todo-checkbox";
  checkbox.checked = todo.completed;
  checkbox.setAttribute("aria-label", `Mark "${todo.title}" as ${todo.completed ? "incomplete" : "complete"}`);
  checkbox.addEventListener("change", () => toggleTodo(todo.id, checkbox.checked));

  // Text block
  const textDiv = document.createElement("div");
  textDiv.className = "todo-text";

  const titleEl = document.createElement("span");
  titleEl.className = "todo-title";
  titleEl.textContent = todo.title;
  textDiv.appendChild(titleEl);

  if (todo.description) {
    const descEl = document.createElement("p");
    descEl.className = "todo-description";
    descEl.textContent = todo.description;
    textDiv.appendChild(descEl);
  }

  // Actions
  const actionsDiv = document.createElement("div");
  actionsDiv.className = "todo-actions";

  const deleteBtn = document.createElement("button");
  deleteBtn.className = "btn-icon btn-delete";
  deleteBtn.textContent = "Delete";
  deleteBtn.setAttribute("aria-label", `Delete "${todo.title}"`);
  deleteBtn.addEventListener("click", () => deleteTodo(todo.id));

  actionsDiv.appendChild(deleteBtn);

  li.appendChild(checkbox);
  li.appendChild(textDiv);
  li.appendChild(actionsDiv);

  return li;
}

// ── CRUD operations ────────────────────────────────────────────────────────
async function createTodo(title, description) {
  const body = { title };
  if (description) body.description = description;
  const created = await apiRequest("POST", "/todos", body);
  if (created) {
    todos.push(created);
    renderTodos();
  }
}

async function toggleTodo(id, completed) {
  const updated = await apiRequest("PUT", `/todos/${id}`, { completed });
  if (updated) {
    todos = todos.map((t) => (t.id === id ? updated : t));
    renderTodos();
  }
}

async function deleteTodo(id) {
  await apiRequest("DELETE", `/todos/${id}`);
  todos = todos.filter((t) => t.id !== id);
  renderTodos();
}

// ── Event listeners ────────────────────────────────────────────────────────
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = titleInput.value.trim();
  const description = descInput.value.trim();
  if (!title) return;

  await createTodo(title, description);
  form.reset();
  titleInput.focus();
});

filterButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    filterButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    activeFilter = btn.dataset.filter;
    renderTodos();
  });
});

// ── Boot ───────────────────────────────────────────────────────────────────
loadTodos();
