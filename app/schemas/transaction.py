from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):
    transaction_type: Literal["credit", "debit"]
    amount_kobo: int = Field(
        gt=0,
        examples=[50000],
    )


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    wallet_id: UUID
    transaction_type: Literal["credit", "debit"]
    amount_kobo: int
    created_at: datetime