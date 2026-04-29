import logging
from uuid import UUID

from app.core.config import settings
from app.core.exceptions import AIAnalysisError
from app.services.ai_analysis_service import create_ai_analysis
from app.services.ai_analyzer import analyze_email
from app.services.email_service import get_email_by_id
from app.services.reply_service import create_draft_reply
from app.services.workflow_engine import create_workflow_from_analysis
from app.services.reply_policy_service import should_auto_send_reply
from app.services.reply_send_workflow import approve_and_send_reply

logger = logging.getLogger(__name__)


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

    detected_category = (analysis.category or "").strip().lower()
    allowed_categories = settings.allowed_categories_set

    if detected_category not in allowed_categories:
        email.processing_status = "ignored_category"
        session.add(email)
        await session.commit()

        logger.info(
            "email filtered by category: email_id=%s category=%s allowed=%s",
            email.id,
            detected_category,
            sorted(allowed_categories),
        )

        return {
            "analysis": analysis,
            "workflow": None,
            "reply": None,
            "filtered": True,
            "filter_reason": f"category_not_allowed:{detected_category}",
        }

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

    policy = should_auto_send_reply(analysis=analysis, reply=reply)

    auto_send_executed = False
    auto_send_result = None

    if policy.allow_auto_send:
        auto_send_executed = True
        auto_send_result = await approve_and_send_reply(
            session=session,
            reply_id=reply.id,
            approved_by="system_auto_send",
        )
        reply = auto_send_result

    await session.commit()
    await session.refresh(reply)

    return {
        "analysis": analysis,
        "workflow": workflow,
        "reply": reply,
        "filtered": False,
        "filter_reason": None,
        "auto_send_executed": auto_send_executed,
        "auto_send_reason": policy.reason,
    }
    
