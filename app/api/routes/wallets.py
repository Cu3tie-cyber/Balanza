from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.transaction import Transaction
from app.models.wallet import Wallet
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.schemas.wallet import WalletCreate, WalletResponse


router = APIRouter(prefix="/wallets", tags=["wallets"])


@router.post(
    "",
    response_model=WalletResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_wallet(
    wallet_data: WalletCreate,
    db: Session = Depends(get_db),
) -> Wallet:
    wallet = Wallet(
        name=wallet_data.name,
        currency=wallet_data.currency,
    )

    db.add(wallet)
    db.commit()
    db.refresh(wallet)

    return wallet


@router.get(
    "/{wallet_id}",
    response_model=WalletResponse,
)
def get_wallet(
    wallet_id: UUID,
    db: Session = Depends(get_db),
) -> Wallet:
    wallet = db.get(Wallet, wallet_id)

    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    return wallet


@router.post(
    "/{wallet_id}/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    wallet_id: UUID,
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
) -> Transaction:
    try:
        wallet = db.scalar(
            select(Wallet)
            .where(Wallet.id == wallet_id)
            .with_for_update()
        )

        if wallet is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found",
            )

        if (
            transaction_data.transaction_type == "debit"
            and wallet.balance_kobo < transaction_data.amount_kobo
        ):
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient wallet balance",
            )

        if transaction_data.transaction_type == "credit":
            wallet.balance_kobo += transaction_data.amount_kobo
        else:
            wallet.balance_kobo -= transaction_data.amount_kobo

        transaction = Transaction(
            wallet_id=wallet.id,
            transaction_type=transaction_data.transaction_type,
            amount_kobo=transaction_data.amount_kobo,
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return transaction

    except HTTPException:
        raise

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to process transaction",
        )


@router.get(
    "/{wallet_id}/transactions",
    response_model=list[TransactionResponse],
)
def list_transactions(
    wallet_id: UUID,
    db: Session = Depends(get_db),
) -> list[Transaction]:
    wallet = db.get(Wallet, wallet_id)

    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    transactions = db.scalars(
        select(Transaction)
        .where(Transaction.wallet_id == wallet_id)
        .order_by(Transaction.created_at.desc())
    ).all()

    return list(transactions)