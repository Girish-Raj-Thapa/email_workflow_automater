from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class SentReplyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email_id: UUID
    analysis_id: UUID
    reply_subject: str
    reply_body: str
    status: str
    created_at: datetime


class ReplyRead(SentReplyRead):
    approved_by: str | None = None
    provider: str | None = None
    provider_message_id: str | None = None
    sent_at: datetime | None = None
    error_message: str | None = None
    attempt_count: int
    
