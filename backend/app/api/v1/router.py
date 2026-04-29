from fastapi import APIRouter

from app.api.v1.endpoints.ai_analysis import router as ai_analysis_router
from app.api.v1.endpoints.emails import router as emails_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.replies import router as replies_router
from app.api.v1.endpoints.workflows import router as workflows_router
from app.api.v1.endpoints import operations

api_router = APIRouter()

api_router.include_router(health_router, tags=["Health"])
api_router.include_router(emails_router, tags=["Emails"])
api_router.include_router(ai_analysis_router, tags=["AI Analysis"])
api_router.include_router(workflows_router, tags=["Workflows"])
api_router.include_router(replies_router, tags=["Replies"])
api_router.include_router(operations.router, tags=["operations"])
