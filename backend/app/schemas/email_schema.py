from datetime import datetime
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import SQLModel

class EmailBase(SQLModel):
    sender_email: EmailStr
    subject: str
    body: str


class EmailCreate(EmailBase):
    pass


class EmailRead(EmailBase):
    id: UUID
    processing_status: str
    received_at: datetime
    