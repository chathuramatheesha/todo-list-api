# Todo List API

A simple and efficient RESTful API for managing tasks in a Todo list application. This API allows you to create, read, update, and delete tasks.

## Features

- Create a task with a title, description, completion status, and due date.
- Retrieve all tasks or a single task by ID.
- Update task details, including the completion status.
- Delete tasks.

## Tech Stack

- **Backend**: Python 3.13.2
- **Framework**: FastAPI
- **Database**: SQLite (via SQLAlchemy)
- **Async I/O**: SQLAlchemy Async API for asynchronous database operations.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/chathuramatheesha/todo-list-api.git
   cd todo-list-api

2. Set up a virtual environment and activate it:
   ```bash
   # For macos/Linux
   python -m venv .venv
   source .venv/bin/activate
   ```
   ```shell
   # For windows powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run Fastapi Application:
   ```bash
   uvicorn app.main:app
   ```

# API Endpoints

## 1. **Create Task**

**POST** `/tasks`

### Request Body
```json
{
  "title": "Test Title",
  "description": "Test Description",
  "due_date": "2025-03-28T08:32:35.626000"
}
```

### Response Body
```json
{
  "title": "Test Title",
  "description": "Test Description",
  "due_date": "2025-03-28T08:32:35.626000",
  "id": 5,
  "is_complete": false
}
```

## 2. **Get Tasks**

**GET** `/tasks`

### Response Body
```json
[
  {
    "title": "string",
    "description": "string",
    "due_date": "2025-03-28T07:13:17.896000",
    "id": 2,
    "is_complete": false
  },
  {
    "title": "string",
    "description": "string",
    "due_date": "2025-03-28T07:13:17.896000",
    "id": 3,
    "is_complete": false
  }
]
```

## 3. **Get Task**

**GET** `/tasks/{task_id}`

### Response Body
```json
{
  "title": "Test Title",
  "description": "Test Description",
  "due_date": "2025-03-28T08:32:35.626000",
  "id": 6,
  "is_complete": false
}
```

## 4. **Update Task**

**PATCH** `/tasks/{task_id}`

### Request Body
```json
{
  "title": "Updated Title",
  "description": "Updated Description",
  "is_complete": false
}
```

### Response Body
```json
{
  "title": "Updated Title",
  "description": "Updated Description",
  "due_date": "2025-03-28T08:32:35.626000",
  "id": 6,
  "is_complete": false
}
```

## 5. **Delete Task**

**DELETE** `/tasks/{task_id}`

### Response Body
```json
{
  "status": "ok",
  "message": "Task deleted successfully"
}
```