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
4. Add environment variables
   - Make sure to create a .env file with the following variables
   ```ini
   SECRET_KEY=<your_secret_key>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   DATABASE_URL=<your_database_url> # mysql or sqlite (default sqlite) # I will update repo for postgres through new branch
   DATABASE_ECHO=True 
   ```

5. Run Fastapi Application:
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
- **Description**: Fetches a list of tasks for the authenticated user. You can filter tasks based on query parameters such as `status`, `priority`, and `due_date`.

#### Query Parameters:

| Parameter          | Type       | Description                                             | Example                                      |
|--------------------|------------|---------------------------------------------------------|----------------------------------------------|
| `filter_status`    | string     | Filter tasks by their status (pending, completed).      | `status=pending`                            |
| `filteer_priority` | string     | Filter tasks by their priority (low, medium, high).     | `priority=high`                             |
| `page`             | integer    | The page number to paginate results. Defaults to 1.     | `page=2`                                    |
| `page_size`        | integer    | The number of tasks per page. Defaults to 10.           | `page_size=20`                              |

#### Example Request:

```bash
GET /tasks?filter_status=pending&filter_priority=high&due_date=2025-04-01&page=1&page_size=10
```

### Response Body
```json
{
  "page_number": 1,
  "page_size": 2,
  "total_items": 4,
  "total_pages": 2,
  "tasks": [
    {
      "title": "Test Title",
      "description": "Test desc",
      "priority": "medium",
      "due_date": "2025-04-30T08:45:02.790000",
      "id": 1,
      "status": "pending"
    },
    {
      "title": "test tititl",
      "description": "string",
      "priority": "low",
      "due_date": "2025-03-30T10:18:13.613000",
      "id": 4,
      "status": "pending"
    }
  ]
}
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