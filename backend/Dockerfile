FROM python:3.11-slim AS base

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Development Stage ---
FROM base AS development
# Install dev dependencies if needed (e.g., for testing)
# COPY requirements-dev.txt .
# RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .
ENV PORT=8000
EXPOSE 8000

# Run with hot-reloading
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# --- Production Stage ---
FROM base AS production
COPY . .

# Cloud Run requires PORT env var
ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
