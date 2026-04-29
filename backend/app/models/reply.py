from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class SentReply(SQLModel, table=True):
    __tablename__ = "sent_replies"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    email_id: UUID = Field(foreign_key="emails.id", index=True)
    analysis_id: UUID = Field(foreign_key="ai_email_analyses.id", index=True)
    reply_subject: str = Field(max_length=255)
    reply_body: str
    status: str = Field(default="drafted", max_length=50)
    approved_by: str | None = Field(default=None, max_length=255)
    provider: str | None = Field(default="smtp", max_length=50)
    provider_message_id: str | None = Field(default=None, max_length=255, index=True)
    sent_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    error_message: str | None = Field(default=None)
    attempt_count: int = Field(default=0)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )