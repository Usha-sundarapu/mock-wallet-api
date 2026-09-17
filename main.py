import os
from dotenv import load_dotenv

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal
from database import SessionLocal
from models import User, Merchant, Transaction
from auth import create_token, verify_token
load_dotenv()
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
app = FastAPI()
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    user_id = verify_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return user_id
class PaymentRequest(BaseModel):
    user_id: int
    merchant_id: int
    amount: Decimal
class LoginRequest(BaseModel):
    user_id: int
class WebhookRequest(BaseModel):
    transaction_id: int
    status: str
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "Mock Wallet API is running!"}


@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@app.post("/login")
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == login_data.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    token = create_token(user.id)

    return {
        "message": "Login successful",
        "user_id": user.id,
        "access_token": token,
        "token_type": "bearer"
    }

@app.post("/webhooks/payment")
def payment_webhook(
    webhook: WebhookRequest,
    webhook_secret: str
):
    if webhook_secret != WEBHOOK_SECRET:
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook secret"
        )

    return {
        "message": "Webhook received",
        "transaction_id": webhook.transaction_id,
        "status": webhook.status
    }

@app.post("/initialize-payment")
def initialize_payment(
    payment: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):

    if current_user != payment.user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only make payments from your own account"
        )

    # Check if user exists
    user = db.query(User).filter(
        User.id == payment.user_id
    ).with_for_update().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if merchant exists
    merchant = db.query(Merchant).filter(
        Merchant.id == payment.merchant_id
    ).first()

    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    # Check amount
    if payment.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    # Check balance
    if user.balance < payment.amount:

        transaction = Transaction(
            sender_id=payment.user_id,
            receiver_id=payment.merchant_id,
            amount=payment.amount,
            status="FAILED"
        )

        db.add(transaction)
        db.commit()

        return {
            "message": "Payment failed",
            "reason": "Insufficient balance",
            "status": "FAILED"
        }

    # Deduct money from user's balance
    user.balance -= payment.amount

    # Create successful transaction
    transaction = Transaction(
        sender_id=payment.user_id,
        receiver_id=payment.merchant_id,
        amount=payment.amount,
        status="SUCCESS"
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return {
        "message": "Payment successful",
        "transaction_id": transaction.id,
        "status": "SUCCESS",
        "amount": payment.amount
    }