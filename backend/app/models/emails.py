from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy import Column, DateTime, UniqueConstraint
from sqlmodel import Field, SQLModel


class Email(SQLModel, table=True):
    __tablename__ = "emails"
    __table_args__ = (
        UniqueConstraint("provider", "provider_message_id", name="uq_email_provider_message"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    sender_email: EmailStr = Field(index=True, max_length=255)
    subject: str = Field(max_length=255)
    body: str
    processing_status: str = Field(default="received", max_length=50)
    source: str = Field(default="api_submission", max_length=50)
    provider: str | None = Field(default=None, max_length=50, index=True)
    provider_message_id: str | None = Field(default=None, max_length=255, index=True)
    thread_id: str | None = Field(default=None, max_length=255, index=True)
    in_reply_to: str | None = Field(default=None, max_length=255)

    received_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    received_raw_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )