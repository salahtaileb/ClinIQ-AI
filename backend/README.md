This folder contains a minimal FastAPI service for ClinIQ-AI.

Endpoints:
- GET /health -&gt; {"status": "ok"}
- POST /predict -&gt; Accepts JSON, returns a fixed dummy prediction

Run locally with: docker compose up --build
