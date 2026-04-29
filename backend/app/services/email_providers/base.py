from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass
class ProviderEmailMessage:
    provider: str
    provider_message_id: str
    sender_email: str
    subject: str
    body: str
    thread_id: str | None = None
    in_reply_to: str | None = None
    received_raw_at: datetime | None = None


class EmailProvider(Protocol):
    async def fetch_messages(self, limit: int) -> list[ProviderEmailMessage]:
        """Fetch latest messages from provider."""
        ...
        