from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WalletCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
        examples=["Main Wallet"],
    )
    currency: str = Field(
        default="NGN",
        min_length=3,
        max_length=3,
        examples=["NGN"],
    )


class WalletResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    currency: str
    balance_kobo: int
    created_at: datetime
    updated_at: datetime