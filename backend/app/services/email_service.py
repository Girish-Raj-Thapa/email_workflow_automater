from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.exceptions import EmailNotFoundError
from app.models.emails import Email
from app.schemas.email_schema import EmailCreate


async def create_email(session: AsyncSession, payload: EmailCreate) -> Email:
    email = Email(
        sender_email=payload.sender_email,
        subject=payload.subject,
        body=payload.body,
    )

    session.add(email)
    await session.commit()
    await session.refresh(email)

    return email


async def list_emails(session: AsyncSession) -> list[Email]:
    statement = select(Email).order_by(Email.received_at.desc())
    result = await session.execute(statement)
    return list(result.scalars().all())


async def get_email_by_id(session: AsyncSession, email_id: UUID) -> Email:
    statement = select(Email).where(Email.id == email_id)
    result = await session.execute(statement)
    email = result.scalar_one_or_none()

    if email is None:
        raise EmailNotFoundError("Email not found")

    return email