import os
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr

# PUBLIC_INTERFACE
def get_settings() -> Dict[str, Any]:
    """Load settings from environment variables."""
    return {
        "SERVICE_NAME": os.getenv("NOTIFICATION_SERVICE_NAME", "Notification Service"),
        "ENV": os.getenv("ENV", "development"),
        "ALLOWED_ORIGINS": os.getenv("ALLOWED_ORIGINS", "*"),
        # Email provider configuration (mock by default)
        "EMAIL_PROVIDER": os.getenv("EMAIL_PROVIDER", "mock"),
        "EMAIL_API_KEY": os.getenv("EMAIL_API_KEY"),
        "EMAIL_FROM": os.getenv("EMAIL_FROM", "no-reply@example.com"),
    }

settings = get_settings()

app = FastAPI(
    title="Notification Service",
    description="Handles transactional email notifications.",
    version="1.0.0",
    openapi_tags=[
        {"name": "health", "description": "Health checks"},
        {"name": "notifications", "description": "Notification APIs"},
    ],
)

allow_origins = [o.strip() for o in settings["ALLOWED_ORIGINS"].split(",")] if settings["ALLOWED_ORIGINS"] else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SendEmailRequest(BaseModel):
    to_email: EmailStr = Field(..., description="Recipient email")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email plaintext body")
    template_id: Optional[str] = Field(None, description="Provider-specific optional template id")

class SendEmailResponse(BaseModel):
    status: str = Field(..., description="Result status")
    provider_id: Optional[str] = Field(None, description="Provider message id")


@app.get("/health", tags=["health"], summary="Liveness", description="Return liveness info.")
async def health():
    return {"status": "ok", "service": settings["SERVICE_NAME"], "env": settings["ENV"], "provider": settings["EMAIL_PROVIDER"]}


def _mock_send(_: SendEmailRequest) -> SendEmailResponse:
    """Mock provider that 'succeeds' and returns a fake id."""
    return SendEmailResponse(status="sent", provider_id="mock-12345")


def _provider_send(req: SendEmailRequest) -> SendEmailResponse:
    """Abstraction layer to send email using configured provider."""
    provider = settings["EMAIL_PROVIDER"].lower()
    if provider == "mock":
        return _mock_send(req)
    # Here you'd add real provider integrations (e.g., SendGrid, SES, Mailgun) using EMAIL_API_KEY.
    # For security, never log sensitive keys.
    return _mock_send(req)


# PUBLIC_INTERFACE
@app.post("/api/v1/notifications/send", tags=["notifications"], summary="Send an email", response_model=SendEmailResponse)
async def send_email(payload: SendEmailRequest):
    try:
        res = _provider_send(payload)
        return res
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
