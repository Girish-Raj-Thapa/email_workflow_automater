import email 
import imaplib
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

from app.core.config import settings
from app.services.email_providers.base import ProviderEmailMessage


def _decode_header_value(value: str | None) -> str:
    if not value:
        return ""
    decoded_parts = email.header.decode_header(value)
    chunks: list[str] = []
    for text, encoding in decoded_parts:
        if isinstance(text, bytes):
            chunks.append(text.decode(encoding or "utf-8", errors="replace"))
        else:
            chunks.append(text)
    return "".join(chunks).strip()


def _extract_text_body(msg: email.message.Message) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue
                charset = part.get_content_charset() or "utf-8"
                return payload.decode(charset, errors="replace").strip()
        return ""
    
    payload = msg.get_payload(decode=True)
    if payload is None:
        return ""
    charset = msg.get_content_charset() or "utf-8"
    return payload.decode(charset, errors="replace").strip()


class ImapProvider:
    provider_name = "imap"

    def _fetch_messages_sync(self, limit: int) -> list[ProviderEmailMessage]:
        if settings.imap_use_ssl:
            client = imaplib.IMAP4_SSL(settings.imap_host, settings.imap_port)
        else:
            client = imaplib.IMAP4(settings.imap_host, settings.imap_port)

        client.login(settings.imap_username, settings.imap_password)
        client.select(settings.imap_folder)

        status, data = client.search(None, "ALL")
        if status != "OK":
            client.logout()
            return []

        all_ids = data[0].split()
        target_ids = all_ids[-limit:]

        messages: list[ProviderEmailMessage] = []
        for msg_id in target_ids:
            fetch_status, raw_data = client.fetch(msg_id, "(RFC822)")
            if fetch_status != "OK":
                continue

            if not raw_data or not isinstance(raw_data[0], tuple):
                continue

            raw_bytes = raw_data[0][1]
            parsed = email.message_from_bytes(raw_bytes)

            message_id = _decode_header_value(parsed.get("Message-ID")) or msg_id.decode()
            sender = _decode_header_value(parsed.get("From"))
            subject = _decode_header_value(parsed.get("Subject"))
            in_reply_to = _decode_header_value(parsed.get("In-Reply-To")) or None
            body = _extract_text_body(parsed)

            received_raw_at = None
            raw_date = parsed.get("Date")
            if raw_date:
                try:
                    dt = parsedate_to_datetime(raw_date)
                    received_raw_at = dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
                except Exception:
                    received_raw_at = datetime.now(timezone.utc)

            messages.append(
                ProviderEmailMessage(
                    provider=self.provider_name,
                    provider_message_id=message_id,
                    sender_email=sender,
                    subject=subject or "(no subject)",
                    body=body or "",
                    thread_id=None,
                    in_reply_to=in_reply_to,
                    received_raw_at=received_raw_at,
                )
            )

        client.logout()
        return messages
    
    async def fetch_messages(self, limit: int) -> list[ProviderEmailMessage]:
        # For Phase 1 simplicity, keep IMAP operations sync but exposed through async method.
        # If needed later, move this to a threadpool.
        return self._fetch_messages_sync(limit=limit)
        