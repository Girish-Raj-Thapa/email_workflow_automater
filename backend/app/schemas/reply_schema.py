from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel


class SentReplyRead(SQLModel):
    id: UUID
    email_id: UUID
    analysis_id: UUID
    reply_subject: str
    reply_body: str
    status: str
    created_at: datetime
