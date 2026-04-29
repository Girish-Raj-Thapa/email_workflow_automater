import asyncio
import logging

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.services.email_ingestion_service import ingest_provider_message
from app.services.email_providers.imap_provider import ImapProvider

logger = logging.getLogger(__name__)


def _build_provider():
    if settings.mail_provider == "imap":
        return ImapProvider()
    raise ValueError(f"Unsupported mail provider: {settings.mail_provider}")


async def run_mail_sync_once() -> None:
    provider = _build_provider()
    messages = await provider.fetch_messages(limit=settings.imap_fetch_limit)

    if not messages:
        logger.info("mail_sync: no messages fetched")
        return

    async with AsyncSessionLocal() as session:
        for msg in messages:
            try:
                outcome = await ingest_provider_message(session=session, message=msg)
                logger.info("mail_sync outcome: %s", outcome)
            except Exception as exc:
                logger.exception(
                    "mail_sync failed for provider_message_id=%s: %s",
                    msg.provider_message_id,
                    exc,
                )


async def mail_sync_loop(stop_event: asyncio.Event) -> None:
    logger.info(
        "mail_sync loop started: enabled=%s interval=%ss provider=%s",
        settings.mail_sync_enabled,
        settings.mail_poll_interval_seconds,
        settings.mail_provider,
    )
    while not stop_event.is_set():
        try:
            await run_mail_sync_once()
        except Exception as exc:
            logger.exception("mail_sync loop error: %s", exc)
        await asyncio.wait_for(
            stop_event.wait(),
            timeout=settings.mail_poll_interval_seconds,
        )

