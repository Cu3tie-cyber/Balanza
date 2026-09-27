from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status

from app.schemas.wallet import WalletCreate, WalletResponse

router = APIRouter(prefix="/wallets", tags=["wallets"])

wallets: dict[UUID, WalletResponse] = {}


@router.post(
    "",
    response_model=WalletResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_wallet(wallet_data: WalletCreate) -> WalletResponse:
    wallet_id = uuid4()

    wallet = WalletResponse(
        id=wallet_id,
        name=wallet_data.name,
        currency=wallet_data.currency,
        balance_kobo=0,
    )

    wallets[wallet_id] = wallet
    return wallet


@router.get(
    "/{wallet_id}",
    response_model=WalletResponse,
)
def get_wallet(wallet_id: UUID) -> WalletResponse:
    wallet = wallets.get(wallet_id)

    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    return wallet