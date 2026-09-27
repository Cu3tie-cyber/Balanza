from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class WalletCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        examples=["Belle's primary wallet"],
    )
    currency: Literal["NGN"] = "NGN"


class WalletResponse(BaseModel):
    id: UUID
    name: str
    currency: Literal["NGN"]
    balance_kobo: int = Field(ge=0)