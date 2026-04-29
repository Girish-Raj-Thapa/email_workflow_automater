from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.emails import Email
from app.models.reply import SentReply
from app.services.smtp_sender_service import send_email_via_smtp


ALLOWED_SEND_STATUSES = {"drafted", "failed"}


async def _get_reply_or_404(session: AsyncSession, reply_id: UUID) -> SentReply:
    reply = await session.get(SentReply, reply_id)
    if reply is None:
        raise NotFoundError("Reply not found")
    return reply


async def _get_email_or_404(session: AsyncSession, email_id: UUID) -> Email:
    email = await session.get(Email, email_id)
    if email is None:
        raise NotFoundError("Email not found")
    return email


async def approve_and_send_reply(
    session: AsyncSession,
    reply_id: UUID,
    approved_by: str,
) -> SentReply:
    reply = await _get_reply_or_404(session=session, reply_id=reply_id)

    if reply.status not in ALLOWED_SEND_STATUSES:
        raise ConflictError(f"Reply with status '{reply.status}' cannot be sent")

    email = await _get_email_or_404(session=session, email_id=reply.email_id)

    # status progression
    reply.status = "approved"
    reply.approved_by = approved_by
    session.add(reply)
    await session.commit()
    await session.refresh(reply)

    reply.status = "queued"
    reply.error_message = None
    reply.attempt_count += 1
    session.add(reply)
    await session.commit()
    await session.refresh(reply)

    try:
        provider_message_id = send_email_via_smtp(
            to_email=email.sender_email,
            subject=reply.reply_subject,
            body=reply.reply_body,
        )

        reply.provider = "smtp"
        reply.provider_message_id = provider_message_id
        reply.sent_at = datetime.now(timezone.utc)
        reply.status = "sent"
        reply.error_message = None
    except Exception as exc:
        reply.status = "failed"
        reply.error_message = str(exc)

    session.add(reply)
    await session.commit()
    await session.refresh(reply)
    return reply


async def retry_send_reply(
    session: AsyncSession,
    reply_id: UUID,
) -> SentReply:
    reply = await _get_reply_or_404(session=session, reply_id=reply_id)

    if reply.status != "failed":
        raise ConflictError("Retry is allowed only when reply status is 'failed'")

    return await approve_and_send_reply(
        session=session,
        reply_id=reply_id,
        approved_by="system_retry",
    )
