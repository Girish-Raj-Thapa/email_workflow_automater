from pydantic import BaseModel, Field


class ApproveSendReplyRequest(BaseModel):
    approved_by: str = Field(min_length=1, max_length=255)
    