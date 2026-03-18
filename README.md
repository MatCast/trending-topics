# Trend Finder Dashboard

A full-stack web application designed to identify trending topics from Reddit, Hacker News, Bluesky and others.

## Features
- **Multi-Source Research**: Fetches real-time trends from Reddit subreddits, Hacker News Top stories, and Bluesky.
- **Personalized Configuration**: Each user can configure their own sources, search keywords, and preferences.
- **Smart Scoring**: Topics are ranked based on engagement (upvotes, comments) and configurable source weights.
- **Automated Scheduling**: Configure your own extraction schedule (Hourly, Daily, Weekly).
- **CSV Export**: Export trending topics for further analysis or drafting.
- **Google Sign-In**: Secure access using your Google account.

## Project Structure
This project is organized as a monorepo:
- `/backend`: FastAPI Python service handling trend parsing, Firestore persistence, and scheduling logic.
- `/frontend`: Nuxt 4 web application using DaisyUI for a premium, responsive experience.

## Quick Start

### 1. Prerequisites
- Node.js 20+
- Python 3.11+
- A Google Cloud Project with Firebase enabled (Firestore + Auth).

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your Firebase service account JSON to backend/keys/
uvicorn app.main:app --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env
# Fill in your Firebase web config in .env
npm run dev
```

Both components are containerized and ready for **Google Cloud Run**.
- Use the provided `Dockerfile` in each directory.
- Configure Cloud Scheduler to trigger the internal extraction endpoint for automated runs.

## 🐳 Running with Docker (Local)

To run the entire application (frontend + backend) locally using Docker Compose:

1.  **Ensure you have Docker and Docker Compose installed.**
2.  **Verify environment variables** in both `backend/.env` and `frontend/.env`.
3.  **Run the application**:
    ```bash
    docker-compose up --build
    ```

- **Backend**: Accessible at `http://localhost:8000`.
- **Frontend**: Accessible at `http://localhost:3000`.
- **Hot-reloading**: Enabled for both services via volume mapping.

## Tech Stack
- **Frontend**: Nuxt 4, Tailwind CSS v4, DaisyUI, Firebase Auth.
- **Backend**: FastAPI, Firestore, Firebase Admin SDK.
- **Infrastucture**: Docker, Google Cloud Run, Cloud Scheduler.

## 🚀 Deployment to Google Cloud Run

This project is configured for seamless deployment to **Google Cloud Run** in the `europe-west1` region.

### 1. Prerequisites
- Install the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install).
- Authenticate and set your project:
  ```bash
  gcloud auth login
  gcloud config set project trending-news-finder
  ```

### 2. Configuration (`.env.yaml`)
Instead of standard `.env` files, use YAML for production environment variables.

**Backend (`backend/.env.yaml`):**
```yaml
ENV: "production"
INTERNAL_API_KEY: "your-shared-secret"
FRONTEND_URL: "https://your-frontend-url.run.app"
# (Other variables from .env.example)
```

**Frontend (`frontend/.env.yaml`):**
```yaml
NUXT_PUBLIC_API_BASE_URL: "https://your-backend-url.run.app"
# (Firebase config variables from .env.example)
```

### 3. Deploy Commands

Deploy from the root of each service:

**Deploy Backend:**
```bash
cd backend
gcloud run deploy backend-service \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --env-vars-file .env.yaml
  --memory 512Mi
```

**Deploy Frontend:**
```bash
cd ../frontend
gcloud run deploy frontend-service \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --env-vars-file .env.yaml
```

### 4. Post-Deployment
1. **CORS**: Ensure the backend's `FRONTEND_URL` in `.env.yaml` includes the actual frontend URL.
2. **Firebase Auth**: Add your frontend URL to the **Authorized Domains** list in the Firebase Console.
3. **Scheduler**: Configure a Cloud Scheduler job to hit `/api/extract/scheduled` using an OIDC token or `X-Internal-Key` header.
