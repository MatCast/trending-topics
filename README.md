# Trend Finder Dashboard

A full-stack web application designed to identify trending topics from Reddit, Hacker News, and Bluesky to help you create viral LinkedIn content.

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

## Deployment
Both components are containerized and ready for **Google Cloud Run**.
- Use the provided `Dockerfile` in each directory.
- Configure Cloud Scheduler to trigger the internal extraction endpoint for automated runs.

## Tech Stack
- **Frontend**: Nuxt 4, Tailwind CSS v4, DaisyUI, Firebase Auth.
- **Backend**: FastAPI, Firestore, Firebase Admin SDK.
- **Infrastucture**: Docker, Google Cloud Run, Cloud Scheduler.

