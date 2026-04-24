from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.reply_schema import SentReplyRead
from app.services.reply_service import get_reply_by_id, list_replies

router = APIRouter()


@router.get("/replies", response_model=list[SentReplyRead])
async def list_replies_endpoint(
    session: AsyncSession = Depends(get_session),
):
    return await list_replies(session=session)


@router.get("/replies/{reply_id}", response_model=SentReplyRead)
async def get_reply_by_id_endpoint(
    reply_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    return await get_reply_by_id(session=session, reply_id=reply_id)
