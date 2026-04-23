from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.exceptions import AIAnalysisAlreadyExistsError, EmailNotFoundError
from app.models.ai_analysis import AIEmailAnalysis
from app.models.emails import Email
from app.schemas.ai_schema import AIEmailAnalysisCreate


async def create_ai_analysis(
    session: AsyncSession,
    email_id: UUID,
    payload: AIEmailAnalysisCreate,
) -> AIEmailAnalysis:

    email_statement = select(Email).where(Email.id == email_id)
    email_result = await session.execute(email_statement)
    email = email_result.scalar_one_or_none()

    if email is None:
        raise EmailNotFoundError("Email not found")

    analysis_statement = select(AIEmailAnalysis).where(AIEmailAnalysis.email_id == email_id)
    analysis_result = await session.execute(analysis_statement)
    existing_analysis = analysis_result.scalar_one_or_none()

    if existing_analysis is not None:
        raise AIAnalysisAlreadyExistsError("AI analysis already exists for this email")

    analysis = AIEmailAnalysis(
        email_id=email_id,
        category=payload.category,
        priority=payload.priority,
        recommended_action=payload.recommended_action,
        assigned_team=payload.assigned_team,
        requires_human_review=payload.requires_human_review,
        confidence=payload.confidence,
        extracted_entities=payload.extracted_entities.model_dump(mode="json"),
        draft_reply=payload.draft_reply,
    )

    email.processing_status = "analyzed"

    session.add(analysis)
    session.add(email)

    await session.commit()
    await session.refresh(analysis)
    await session.refresh(email)

    return analysis
    
