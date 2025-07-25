# Saga AI - The Oracle of Strategy ![Saga AI Banner](https://placehold.co/1200x300/0D0C1D/A78BFA/png?text=Saga%20AI%20-%20The%20Oracle%20of%20Strategy) **Strategy is an Art. I am its Master.** Saga is a full-stack AI application designed to function as an expert strategic consultant. It leverages a sophisticated Retrieval-Augmented Generation (RAG) pipeline, multi-agent architecture, and a resilient, job-based backend to provide deep, actionable insights across multiple business domains. This monorepo contains the complete source code for the Saga AI ecosystem: * `frontend/`: A modern Next.js application serving as the user interface. * `backend/`: A powerful FastAPI backend with Celery workers for asynchronous job processing. --- ## ✨ Features * **🔮 The Grand Strategy:** The core prophecy that analyzes a user's niche and provides a comprehensive go-to-market plan. * **⚒️ The Artisan's Anvil:** A specialized Print-on-Demand (POD) stack that identifies niche design opportunities and generates full AI art prompts and e-commerce listing copy. * **🔮 The Seer's Spire:** A new venture stack that brainstorms and vets 10 unique business ideas from a single user interest, then builds a detailed business plan for a chosen vision. * **🔥 The Skald's Forge:** A marketing stack that generates psychological angles of attack and forges complete marketing assets (ad copy, landing page HTML, email copy). * **💰 The Merchant's Ledger:** A commerce stack providing audits, arbitrage path analysis, and social selling plans. * **🕸️ The Weaver's Loom:** A content stack for generating context-aware social media posts, comments, and blog articles. * **📜 The Grimoire & Scriptorium:** A complete, AI-assisted CMS for managing a public-facing blog, fully integrated into the backend. * **🧠 Persistent Memory:** Saga remembers anonymous user sessions, allowing for a continuous, contextual conversation where each prophecy informs the next. * **🛡️ Resilient Architecture:** All intensive AI generation is handled by background Celery w

B. Frontend Configuration:
Create a file at frontend/.env.local. This file is primarily for local development without Docker. The docker-compose.yml file will override this for containerized development.

Generated env

# frontend/.env.local # For non-Docker local dev, points to the host machine's port 8000 NEXT_PUBLIC_SAGA_API_URL=http://localhost:8000/api/v10 

IGNORE_WHEN_COPYING_START

content_copy download 

Use code with caution. Env

IGNORE_WHEN_COPYING_END

2. Running Locally with Docker (Recommended)

This is the simplest and most reliable way to run the entire Saga ecosystem. From the root directory (where docker-compose.yml is located):

Generated bash

docker-compose up --build 

IGNORE_WHEN_COPYING_START

content_copy download 

Use code with caution. Bash

IGNORE_WHEN_COPYING_END

--build forces Docker to rebuild the images if you've made changes to the code or Dockerfiles.

This single command will start:

The Next.js frontend on http://localhost:3000

The FastAPI backend on http://localhost:8000

The Celery background worker

The Redis message broker

To stop all services, press Ctrl + C in the terminal, and then run docker-compose down.

3. Deploying to Render

This project is optimized for deployment on Render.

Fork this repository to your GitHub account.

Create a New Redis service on Render. Copy its "Internal Connection String".

Create a New "Web Service" for the backend:

Connect your forked repository.

Set the Root Directory to backend.

Set the Start Command to gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.server:app --bind 0.0.0.0:8000.

Under "Environment", add all the keys from your backend/.env file, making sure CELERY_BROKER_URL and CELERY_RESULT_BACKEND point to the internal connection string of your Render Redis service.

Create a New "Background Worker":

Connect the same repository.

Set the Root Directory to backend.

Set the Start Command to celery -A backend.celery_app worker --loglevel=info.

Add the same environment variables as the backend web service.

Create a New "Web Service" for the frontend:

Connect the same repository.

Set the Root Directory to frontend.

Render will detect it's a Next.js app and set build/start commands automatically.

Under "Environment", set NEXT_PUBLIC_SAGA_API_URL to the public URL of your backend web service (e.g., https://saga-backend-123.onrender.com/api/v10).

🔧 Local Development without Docker

If you prefer to run the services manually:

Terminal 1: Start Redis
(Assuming you have Redis installed locally)

Generated bash

redis-server 

IGNORE_WHEN_COPYING_START

content_copy download 

Use code with caution. Bash

IGNORE_WHEN_COPYING_END

Terminal 2: Start the Backend

Generated bash

# Navigate to the backend directory cd backend # Create a virtual environment and install dependencies python -m venv venv source venv/bin/activate # (or .\venv\Scripts\activate on Windows) pip install -r requirements.txt # Start the server uvicorn backend.server:app --reload 

IGNORE_WHEN_COPYING_START

content_copy download 

Use code with caution. Bash

IGNORE_WHEN_COPYING_END

Terminal 3: Start the Celery Worker

Generated bash

# Navigate to the backend directory and activate venv cd backend source venv/bin/activate # Start the worker celery -A backend.celery_app worker --loglevel=info 

IGNORE_WHEN_COPYING_START

content_copy download 

Use code with caution. Bash

IGNORE_WHEN_COPYING_END

Terminal 4: Start the Frontend

Generated bash

# Navigate to the frontend directory cd frontend # Install dependencies and start npm install npm run dev 

IGNORE_WHEN_COPYING_START

content_copy download 

Use code with caution. Bash

IGNORE_WHEN_COPYING_END

📚 API Documentation

Once the backend server is running, interactive API documentation (provided by Swagger UI) is available at:

http://localhost:8000/docs

Generated code

IGNORE_WHEN_COPYING_START

content_copy download 

Use code with caution. 

IGNORE_WHEN_COPYING_END

