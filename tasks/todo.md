# Deployment Task List

## Setup & Configuration (To be done by Agent)
- [x] Update `backend/app/main.py` CORS middleware to parse a comma-separated list of origins.
- [x] Create `backend/.dockerignore` (Crucial: ignore `keys/` directory and `.env`).
- [x] Create `frontend/.dockerignore` (Ignore `node_modules`, `.output`, `.nuxt`, `.env`).
- [x] Update `plan.md` to reflect the deployment phase.

## Security Hardening (To be done by Agent)
- [x] Fix Broken Access Control in `admin.py` by requiring the `user['active_tier'] == 'admin'`.
- [x] Fix Unauthenticated Execution in `extraction.py` by raising a 401 instead of just warning on the `/scheduled` endpoint.
- [x] Disable Swagger UI Docs in production via environment variable fallback.

## Manual User Actions (Post-Setup)
- [ ] Authenticate `gcloud` and set project to `trending-news-finder`.
- [ ] Enable Cloud Run and Cloud Build APIs.
- [ ] Deploy the backend to Cloud Run (without passing `FIREBASE_SERVICE_ACCOUNT_PATH`, using `--env-vars-file env.prod.yaml`).
- [ ] Deploy the frontend to Cloud Run (passing backend URL as `NUXT_PUBLIC_API_BASE_URL` and Firebase config, using `--env-vars-file env.prod.yaml`).
- [ ] Add the frontend `.run.app` domain to Firebase Authentication Authorized Domains.
- [ ] Add the frontend `.run.app` domain to Firebase Authentication Authorized Domains.
