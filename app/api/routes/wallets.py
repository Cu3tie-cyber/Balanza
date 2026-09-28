from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.wallet import Wallet
from app.schemas.wallet import WalletCreate, WalletResponse


router = APIRouter(prefix="/wallets", tags=["wallets"])


def wallet_to_response(wallet: Wallet) -> WalletResponse:
    return WalletResponse(
        id=wallet.id,
        name=wallet.name,
        currency=wallet.currency,
        balance_kobo=wallet.balance_kobo,
    )


@router.post(
    "",
    response_model=WalletResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_wallet(
    wallet_data: WalletCreate,
    db: Session = Depends(get_db),
) -> WalletResponse:
    wallet = Wallet(
        name=wallet_data.name,
        currency=wallet_data.currency,
    )

    db.add(wallet)
    db.commit()
    db.refresh(wallet)

    return wallet_to_response(wallet)


@router.get(
    "/{wallet_id}",
    response_model=WalletResponse,
)
def get_wallet(
    wallet_id: UUID,
    db: Session = Depends(get_db),
) -> WalletResponse:
    wallet = db.get(Wallet, wallet_id)

    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    return wallet_to_response(wallet)