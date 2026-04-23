from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.email_schema import EmailCreate, EmailRead
from app.services.email_service import create_email, get_email_by_id, list_emails

router = APIRouter()


@router.post(
    "/emails",
    response_model=EmailRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_email_endpoint(
    payload: EmailCreate,
    session: AsyncSession = Depends(get_session),
):
    return await create_email(session=session, payload=payload)


@router.get(
    "/emails",
    response_model=list[EmailRead],
)
async def list_emails_endpoint(
    session: AsyncSession = Depends(get_session),
):
    return await list_emails(session=session)


@router.get(
    "/emails/{email_id}",
    response_model=EmailRead,
)
async def get_email_by_id_endpoint(
    email_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    return await get_email_by_id(session=session, email_id=email_id)
    