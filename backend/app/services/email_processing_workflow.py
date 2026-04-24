from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.email_schema import EmailCreate
from app.services.email_analysis_workflow import analyze_email_and_store
from app.services.email_service import create_email


async def process_email_from_submission(
    session: AsyncSession,
    payload: EmailCreate,
):
    email = await create_email(session=session, payload=payload)

    result = await analyze_email_and_store(
        session=session,
        email_id=email.id,
    )

    return {
        "email": email,
        "analysis": result["analysis"],
        "workflow": result["workflow"],
        "reply": result["reply"],
    }
