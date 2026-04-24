from uuid import UUID

from app.core.exceptions import AIAnalysisError
from app.services.ai_analysis_service import create_ai_analysis
from app.services.ai_analyzer import analyze_email
from app.services.email_service import get_email_by_id
from app.services.reply_service import create_draft_reply
from app.services.workflow_engine import create_workflow_from_analysis


async def analyze_email_and_store(session, email_id: UUID):
    email = await get_email_by_id(session=session, email_id=email_id)

    try:
        analysis_payload = await analyze_email(
            subject=email.subject,
            body=email.body,
        )
    except Exception as exc:
        raise AIAnalysisError(f"AI analysis failed: {exc}") from exc

    analysis = await create_ai_analysis(
        session=session,
        email_id=email_id,
        payload=analysis_payload,
    )

    workflow = await create_workflow_from_analysis(
        session=session,
        email=email,
        analysis=analysis,
    )

    reply = await create_draft_reply(
        session=session,
        email=email,
        analysis=analysis,
    )

    await session.commit()
    await session.refresh(reply)

    return {
        "analysis": analysis,
        "workflow": workflow,
        "reply": reply,
    }
