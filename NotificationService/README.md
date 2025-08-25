# Notification Service

Sends transactional emails via provider abstraction (mock by default).

## Run
1. Copy `.env.example` to `.env`.
2. Install deps:

   pip install -r requirements.txt

3. Start:

   uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

## Endpoints
- GET /health
- POST /api/v1/notifications/send
