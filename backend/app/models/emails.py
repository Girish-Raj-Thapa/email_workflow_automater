from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class Email(SQLModel, table=True):
    __tablename__ = "emails"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    sender_email: EmailStr = Field(index=True, max_length=255)
    subject: str = Field(max_length=255)
    body: str
    processing_status: str = Field(default="received", max_length=50)
    received_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    