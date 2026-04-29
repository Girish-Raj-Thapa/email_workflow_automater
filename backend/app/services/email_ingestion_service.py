from email.utils import parseaddr
import re

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.emails import Email
from app.services.email_analysis_workflow import analyze_email_and_store
from app.services.email_providers.base import ProviderEmailMessage


async def email_exists_by_provider_id(
    session: AsyncSession,
    provider: str,
    provider_message_id: str,
) -> bool:
    statement = select(Email.id).where(
        Email.provider == provider,
        Email.provider_message_id == provider_message_id,
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none() is not None


async def ingest_provider_message(
    session: AsyncSession,
    message: ProviderEmailMessage,
) -> dict:
    exists = await email_exists_by_provider_id(
        session=session,
        provider=message.provider,
        provider_message_id=message.provider_message_id,
    )

    if exists:
        return {"status": "skipped_duplicate", "provider_message_id": message.provider_message_id}

    should_ingest, reason = should_ingest_message(message=message)

    if not should_ingest:
        email = Email(
            sender_email=normalize_sender_email(message.sender_email),
            subject=message.subject or "(no subject)",
            body=message.body or "",
            source="mailbox_sync",
            provider=message.provider,
            provider_message_id=message.provider_message_id,
            thread_id=message.thread_id,
            in_reply_to=message.in_reply_to,
            received_raw_at=message.received_raw_at,
            processing_status="ignored_prefilter",
        )
        session.add(email)
        await session.commit()
        await session.refresh(email)

        return {
            "status": "skipped_prefilter",
            "reason": reason,
            "email_id": str(email.id),
            "provider_message_id": message.provider_message_id,
        }

    email = Email(
        sender_email=normalize_sender_email(message.sender_email),
        subject=message.subject or "(no subject)",
        body=message.body or "",
        source="mailbox_sync",
        provider=message.provider,
        provider_message_id=message.provider_message_id,
        thread_id=message.thread_id,
        in_reply_to=message.in_reply_to,
        received_raw_at=message.received_raw_at,
    )
    session.add(email)
    await session.commit()
    await session.refresh(email)

    result = await analyze_email_and_store(
        session=session,
        email_id=email.id,
    )

    return {
        "status": "processed",
        "email_id": str(email.id),
        "analysis_id": str(result["analysis"].id),
        "workflow_id": str(result["workflow"].id) if result["workflow"] else None,
        "reply_id": str(result["reply"].id) if result["reply"] else None,
        "filtered": result.get("filtered", False),
        "filter_reason": result.get("filter_reason"),
    }


def normalize_sender_email(raw_sender: str | None) -> str:
    if not raw_sender:
        return "unknown@example.com"
    _, addr = parseaddr(raw_sender)
    if addr:
        return addr.strip().lower()
    return raw_sender.strip().lower()


def extract_sender_local_and_domain(raw_sender: str | None) -> tuple[str, str]:
    normalized = normalize_sender_email(raw_sender)
    if "@" not in normalized:
        return normalized, ""
    local, domain = normalized.split("@", 1)
    return local, domain


def link_count(text: str) -> int:
    return len(re.findall(r"https?://", text or "", flags=re.IGNORECASE))


def should_ingest_message(message: ProviderEmailMessage) -> tuple[bool, str | None]:
    local, domain = extract_sender_local_and_domain(message.sender_email)
    subject = (message.subject or "").strip().lower()
    body = (message.body or "").strip()
    body_lower = body.lower()

    allowed_domains = settings.allowed_sender_domains_set
    if allowed_domains and domain and domain not in allowed_domains:
        return False, f"blocked_sender_domain:{domain}"

    if local in settings.blocked_sender_prefixes_set:
        return False, f"blocked_sender_prefix:{local}"

    for keyword in settings.blocked_subject_keywords_set:
        if keyword and (keyword in subject or keyword in body_lower):
            return False, f"blocked_keyword:{keyword}"

    if len(body) < settings.mail_min_body_length:
        return False, "body_too_short"

    if link_count(body) > settings.mail_max_link_count:
        return False, "too_many_links"

    return True, None
    
