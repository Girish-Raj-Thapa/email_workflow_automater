from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.ai_schema import AnalyzeEmailResult
from app.services.email_analysis_workflow import analyze_email_and_store

router = APIRouter()


@router.post(
    "/emails/{email_id}/analyze",
    response_model=AnalyzeEmailResult,
    status_code=status.HTTP_201_CREATED,
)
async def analyze_email_endpoint(
    email_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    return await analyze_email_and_store(session=session, email_id=email_id)
    
