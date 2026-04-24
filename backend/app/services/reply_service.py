from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.exceptions import NotFoundError
from app.models.ai_analysis import AIEmailAnalysis
from app.models.emails import Email
from app.models.reply import SentReply


async def create_draft_reply(
    session: AsyncSession,
    email: Email,
    analysis: AIEmailAnalysis,
) -> SentReply:
    reply = SentReply(
        email_id=email.id,
        analysis_id=analysis.id,
        reply_subject=f"Re: {email.subject}",
        reply_body=analysis.draft_reply,
        status="drafted",
    )

    session.add(reply)
    await session.flush()

    return reply


async def list_replies(session: AsyncSession) -> list[SentReply]:
    statement = select(SentReply).order_by(SentReply.created_at.desc())
    result = await session.execute(statement)
    return list(result.scalars().all())


async def get_reply_by_id(session: AsyncSession, reply_id: UUID) -> SentReply:
    statement = select(SentReply).where(SentReply.id == reply_id)
    result = await session.execute(statement)
    reply = result.scalar_one_or_none()

    if reply is None:
        raise NotFoundError("Reply not found")

    return reply
