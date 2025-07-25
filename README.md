# Saga AI - The Oracle of Strategy  
![Saga AI Banner](https://placehold.co/1200x300/0D0C1D/A78BFA/png?text=Saga%20AI%20-%20The%20Oracle%20of%20Strategy)

**Strategy is an Art. I am its Master.**

Saga is a full-stack AI application designed to function as an expert strategic consultant. It leverages a sophisticated Retrieval-Augmented Generation (RAG) pipeline, multi-agent architecture, and a resilient, job-based backend to provide deep, actionable insights across multiple business domains.

This monorepo contains the complete source code for the Saga AI ecosystem:

- `frontend/`: A modern Next.js application serving as the user interface.  
- `backend/`: A powerful FastAPI backend with Celery workers for asynchronous job processing.  

---

## ✨ Features

- **🔮 The Grand Strategy:** Analyzes a user's niche and provides a comprehensive go-to-market plan.
- **⚒️ The Artisan's Anvil:** A specialized Print-on-Demand (POD) stack for generating AI prompts and product listings.
- **🔮 The Seer's Spire:** Brainstorms and vets 10 unique business ideas based on user input, then crafts detailed business plans.
- **🔥 The Skald's Forge:** Generates psychological marketing angles and complete marketing assets.
- **💰 The Merchant's Ledger:** Provides audits, arbitrage path analysis, and social selling strategies.
- **🕸️ The Weaver's Loom:** Context-aware social media posts, comments, and blog articles.
- **📜 The Grimoire & Scriptorium:** AI-assisted CMS for managing a public-facing blog.
- **🧠 Persistent Memory:** Remembers anonymous sessions for contextual, continuous interactions.
- **🛡️ Resilient Architecture:** Celery handles AI tasks in the background for a responsive UI.
- **🐳 Fully Dockerized:** Containerized ecosystem for effortless development and deployment.

---

## 🏛️ Architecture Overview

Saga uses a decoupled, service-oriented model designed for scalability and resilience.

![Architecture Diagram](https://placehold.co/800x450/16152C/E0E0E0/png?text=Frontend%20%E2%86%92%20Backend%20%E2%86%92%20Redis%20%E2%86%92%20Celery%20Worker)

1. **Frontend (Next.js):** React frontend sends requests to the backend.
2. **Backend (FastAPI):** Creates a job and queues it in Redis.
3. **Redis:** Holds the queue of jobs.
4. **Celery Worker:** Executes RAG + LLM logic in the background.
5. **Polling:** Frontend polls for task results until ready.

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/)
- [Node.js](https://nodejs.org/) v20+ (if running frontend manually)
- [Python](https://www.python.org/) 3.11+ (if running backend manually)

---

### 1. Configure Environment Variables

You’ll need two `.env` files:

#### A. Backend Configuration (`backend/.env`)
```env
# backend/.env

# Gemini API Keys (comma-separated)
GEMINI_API_KEYS="YOUR_GEMINI_API_KEY_1,ANOTHER_KEY_IF_YOU_HAVE_ONE"

# MongoDB Connection String
MONGO_URI="mongodb+srv://<user>:<password>@<cluster-uri>/"

# Secret key for admin-only endpoints
ADMIN_API_KEY="generate_a_strong_secret_key"

# Redis connection for Celery (Docker default)
CELERY_BROKER_URL="redis://redis:6379/0"
CELERY_RESULT_BACKEND="redis://redis:6379/0"

# Optional Seers keys
# KEYWORDTOOL_IO_API_KEY="your_optional_key"
```

#### B. Frontend Configuration (`frontend/.env.local`)
```env
# frontend/.env.local

# For local dev (non-Docker)
NEXT_PUBLIC_SAGA_API_URL=http://localhost:8000/api/v10
```

---

### 2. Running Locally with Docker (Recommended)

From the root directory:

```bash
docker-compose up --build
```

This launches:

- Next.js frontend → [http://localhost:3000](http://localhost:3000)  
- FastAPI backend → [http://localhost:8000](http://localhost:8000)  
- Celery background worker  
- Redis message broker  

To stop:
```bash
Ctrl + C
docker-compose down
```

---

### 3. Deploying to Render

Saga is optimized for [Render](https://render.com):

- **Fork this repo** to your GitHub.
- **Create a Redis Service** and copy its internal connection string.
- **Backend Web Service**:
  - Root: `backend`
  - Start Command:
    ```bash
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.server:app --bind 0.0.0.0:8000
    ```
  - Add all backend `.env` variables, including Redis connection.

- **Background Worker**:
  - Root: `backend`
  - Start Command:
    ```bash
    celery -A backend.celery_app worker --loglevel=info
    ```

- **Frontend Web Service**:
  - Root: `frontend`
  - Render will auto-detect Next.js
  - Add:
    ```env
    NEXT_PUBLIC_SAGA_API_URL=https://your-backend.onrender.com/api/v10
    ```

---

## 🔧 Local Development without Docker

#### Terminal 1: Start Redis
```bash
redis-server
```

#### Terminal 2: Start Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate (Windows)
pip install -r requirements.txt
uvicorn backend.server:app --reload
```

#### Terminal 3: Start Celery Worker
```bash
cd backend
source venv/bin/activate
celery -A backend.celery_app worker --loglevel=info
```

#### Terminal 4: Start Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 📚 API Documentation

Once backend is live, view interactive API docs at:

[http://localhost:8000/docs](http://localhost:8000/docs)
