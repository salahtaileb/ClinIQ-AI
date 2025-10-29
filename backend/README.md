This folder contains a minimal FastAPI service for ClinIQ-AI.

Endpoints:
- GET /health -> {"status": "ok"}
- POST /predict -> Accepts JSON, returns a fixed dummy prediction

Run locally with: docker compose up --build
