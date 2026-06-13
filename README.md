# AI-Powered Task & Knowledge Management System

A full-stack web application built with Django, React.js, and MySQL where admins
manage a knowledge base of documents and assign tasks to users. Users complete
tasks using AI-powered semantic search to find relevant information.

---

## Live Demo Credentials

| Role  | Username     | Password     |
|-------|--------------|--------------|
| Admin | admin        | (set via createsuperuser) |
| User  | testuser     | testpass123  |

---

## Tech Stack

| Layer       | Technology                                      |
|-------------|-------------------------------------------------|
| Backend     | Python 3.11, Django 4.x, Django REST Framework  |
| Auth        | JWT via djangorestframework-simplejwt           |
| Database    | MySQL 8.x with relational schema                |
| AI / Search | sentence-transformers (all-MiniLM-L6-v2), FAISS |
| Frontend    | React.js 18, React Router v6, Axios             |
| Permissions | Custom RBAC (Admin / User roles)                |

---

## Features

### Authentication & Security
- JWT-based login with access and refresh tokens
- Role-based access control — Admin and User roles
- All APIs protected by role-specific permission classes
- Passwords hashed via Django's built-in create_user
- Secrets managed via .env file (never committed to Git)

### Admin Capabilities
- Upload .txt documents to the knowledge base
- Documents are automatically embedded and indexed for AI search
- Create tasks and assign them to any registered user
- View all tasks across all users with filtering
- Access analytics dashboard with task stats and search trends

### User Capabilities
- View only their own assigned tasks
- Mark tasks as completed
- Search the knowledge base using AI semantic search
- Results ranked by relevance score (0–100%)

### AI Semantic Search
- Uses sentence-transformers all-MiniLM-L6-v2 model
- Runs fully locally — no external API, no internet required after setup
- Converts documents and queries to 384-dimensional vector embeddings
- Stores embeddings in a FAISS IndexFlatL2 vector database
- Searches by meaning, not just keywords
- Example: searching "fixing errors" finds documents about "debugging issues"

### Task Management
- Admins create tasks with title, description, and assigned user
- Users see only their own tasks on the dashboard
- Status transitions: Pending → Completed
- Dynamic filtering: ?status=completed, ?assigned_to=1

### Activity Logging
Every key action is recorded in the activity_logs table:
- User login (with IP address)
- Document upload
- Search queries
- Task status updates

### Analytics
- Total tasks count
- Completed vs pending breakdown
- Completion percentage with visual progress bar
- Top 5 most searched queries

---

## Project Structure

---

## Database Schema

### users_customuser
| Column     | Type        | Notes                    |
|------------|-------------|--------------------------|
| id         | INT PK      | Auto increment           |
| username   | VARCHAR     | Unique                   |
| email      | VARCHAR     |                          |
| password   | VARCHAR     | Hashed by Django         |
| role       | VARCHAR(10) | 'admin' or 'user'        |
| is_active  | BOOLEAN     | Django default           |
| date_joined| DATETIME    | Django default           |

### tasks_task
| Column      | Type        | Notes                    |
|-------------|-------------|--------------------------|
| id          | INT PK      |                          |
| title       | VARCHAR(255)|                          |
| description | TEXT        |                          |
| status      | VARCHAR(20) | 'pending' or 'completed' |
| assigned_to | INT FK      | → users_customuser.id    |
| created_by  | INT FK      | → users_customuser.id    |
| created_at  | DATETIME    | Auto set on create       |
| updated_at  | DATETIME    | Auto set on update       |

### documents_document
| Column      | Type        | Notes                    |
|-------------|-------------|--------------------------|
| id          | INT PK      |                          |
| title       | VARCHAR(255)|                          |
| file_path   | VARCHAR(500)| Path on disk             |
| content     | TEXT        | Extracted text for AI    |
| uploaded_by | INT FK      | → users_customuser.id    |
| uploaded_at | DATETIME    | Auto set on create       |

### analytics_activitylog
| Column    | Type       | Notes                              |
|-----------|------------|------------------------------------|
| id        | INT PK     |                                    |
| user      | INT FK     | → users_customuser.id              |
| action    | VARCHAR(50)| login, upload, search, task_update |
| detail    | TEXT       | Extra context                      |
| timestamp | DATETIME   | Auto set on create                 |

---

## API Reference

### Auth
| Method | Endpoint              | Auth     | Description           |
|--------|-----------------------|----------|-----------------------|
| POST   | /auth/login/          | Public   | Returns JWT tokens    |
| POST   | /api/auth/register/   | Public   | Create user account   |
| POST   | /auth/refresh/        | Public   | Refresh access token  |

### Users
| Method | Endpoint        | Auth     | Description           |
|--------|-----------------|----------|-----------------------|
| GET    | /api/users/     | Admin    | List all users        |
| GET    | /api/users/me/  | Any user | Current user info     |

### Tasks
| Method | Endpoint                        | Auth     | Description           |
|--------|---------------------------------|----------|-----------------------|
| GET    | /api/tasks/                     | Any user | List tasks by role    |
| POST   | /api/tasks/                     | Admin    | Create task           |
| GET    | /api/tasks/{id}/                | Any user | Task detail           |
| PATCH  | /api/tasks/{id}/                | Any user | Update task status    |
| DELETE | /api/tasks/{id}/                | Admin    | Delete task           |
| GET    | /api/tasks/?status=pending      | Any user | Filter by status      |
| GET    | /api/tasks/?assigned_to=1       | Any user | Filter by user        |

### Documents
| Method | Endpoint          | Auth     | Description           |
|--------|-------------------|----------|-----------------------|
| GET    | /api/documents/   | Any user | List all documents    |
| POST   | /api/documents/   | Admin    | Upload .txt document  |

### Search
| Method | Endpoint               | Auth     | Description              |
|--------|------------------------|----------|--------------------------|
| GET    | /api/search/?q=query   | Any user | AI semantic search       |

### Analytics
| Method | Endpoint          | Auth     | Description              |
|--------|-------------------|----------|--------------------------|
| GET    | /api/analytics/   | Any user | Stats + top searches     |

---

## Setup Instructions

### Prerequisites

Make sure you have these installed:
- Python 3.9 or higher
- Node.js 18 or higher
- MySQL 8.x running locally
- Git

---

### Step 1 — Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-task-system.git
cd ai-task-system
```

---

### Step 2 — Backend setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows

# Install all Python dependencies
pip install -r requirements.txt
```

---

### Step 3 — Create the MySQL database

```bash
mysql -u root -p
```

Inside the MySQL prompt:
```sql
CREATE DATABASE ai_task_db CHARACTER SET utf8mb4;
exit;
```

---

### Step 4 — Configure environment variables

Create a file called `.env` inside the `backend/` folder:
---

### Step 5 — Run migrations

```bash
python manage.py migrate
```

This creates all tables in MySQL. Verify by running:
```bash
mysql -u root -p ai_task_db
SHOW TABLES;
exit;
```

You should see: `users_customuser`, `tasks_task`, `documents_document`, `analytics_activitylog`

---

### Step 6 — Create admin user

```bash
python manage.py createsuperuser
# enter username, email, password when prompted
```

Then set the role to admin:
```bash
python manage.py shell

from users.models import CustomUser
u = CustomUser.objects.get(username='your_admin_username')
u.role = 'admin'
u.save()
exit()
```

---

### Step 7 — Create a test regular user

```bash
python manage.py shell

from users.models import CustomUser
CustomUser.objects.create_user(
    username='testuser',
    password='testpass123',
    role='user'
)
exit()
```

---

### Step 8 — Start the backend server

```bash
python manage.py runserver
```

Backend is running at: `http://127.0.0.1:8000`

---

### Step 9 — Frontend setup

Open a new terminal:

```bash
cd frontend
npm install
npm start
```

Frontend is running at: `http://localhost:3000`

---

### Step 10 — Upload documents and test AI search

1. Log in at `http://localhost:3000/login` with your admin account
2. Go to Documents page and upload a few `.txt` files
3. Go to Search page and search for a concept — the AI finds
   semantically related documents even without exact keyword matches

If you ever need to rebuild the AI index from scratch:
```bash
cd backend
python manage.py rebuild_index
```

---

## How the AI Search Works

The model runs entirely on your local machine. No data is sent to any
external server. No API key required.

---

## Running Tests

### Test all APIs with curl

```bash
# 1. Login
curl -X POST http://127.0.0.1:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}'

# 2. List tasks (use token from step 1)
curl http://127.0.0.1:8000/api/tasks/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Filter tasks
curl "http://127.0.0.1:8000/api/tasks/?status=pending" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Upload document
echo "Python is a programming language." > test.txt
curl -X POST http://127.0.0.1:8000/api/documents/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=Python Guide" -F "file=@test.txt"

# 5. AI search
curl "http://127.0.0.1:8000/api/search/?q=coding+language" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 6. Analytics
curl http://127.0.0.1:8000/api/analytics/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Requirements Checklist

| Requirement                    | Implementation                                    |
|-------------------------------|---------------------------------------------------|
| JWT Authentication             | djangorestframework-simplejwt, /auth/login/       |
| RBAC — Admin role              | IsAdmin permission class, enforced per endpoint   |
| RBAC — User role               | get_queryset() filters by assigned_to=request.user|
| MySQL with relations           | 4 tables with FK relationships                    |
| Document upload (.txt)         | MultiPartParser, saved to media/documents/        |
| AI semantic search             | sentence-transformers + FAISS, fully local        |
| Vector DB                      | FAISS IndexFlatL2, persisted to disk              |
| Task CRUD                      | TaskViewSet with ModelViewSet                     |
| Task assignment                | assigned_to FK, admin sets it on create           |
| Status update Pending→Completed| PATCH /api/tasks/{id}/ with role check            |
| Dynamic filtering API          | django-filter, ?status= and ?assigned_to=         |
| Activity logging — login       | LoggedTokenObtainPairView                         |
| Activity logging — upload      | ActivityLog.objects.create() in DocumentViewSet   |
| Activity logging — search      | ActivityLog.objects.create() in DocumentSearchView|
| Activity logging — task update | ActivityLog.objects.create() in partial_update    |
| Analytics — task counts        | Task.objects.count() queries                      |
| Analytics — top searches       | GROUP BY with annotate(count=Count('id'))         |
| React frontend                 | 6 pages, React Router, Axios with JWT interceptor |
| Clean architecture             | Separate apps, serializers, views, permissions    |

---

## Known Limitations

- File upload supports .txt only (PDF support can be added with pypdf2)
- FAISS index is stored on local disk (can be upgraded to Pinecone or Weaviate
  for production)
- No email verification on registration
- Frontend is not deployed (runs locally only)

---

## Author

Built as a technical assignment demonstrating full-stack Python/React
development with AI/ML integration.

- Backend: Django REST Framework with JWT and RBAC
- Database: MySQL with normalized relational schema  
- AI: Local semantic search with sentence-transformers and FAISS
- Frontend: React.js with role-based UI and JWT auth flow

cd "C:\Users\vishalvk\OneDrive\Attachments\Desktop\project_assignment\ai-task-system"

git add README.md

git commit -m "Add complete README"

git push origin main
https://github.com/vishalkokatnur96/ai-task-system.git
