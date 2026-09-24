from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, get_db
from app.gateways.dummy_upi_gateway import DummyUPIGateway
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.token_repository import TokenRepository
from app.schemas.payment import PaymentRequest, PaymentResponse
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/api/orders", tags=["Payments"])

def response(payment): return PaymentResponse(id=payment.id, order_id=payment.order_id, amount=payment.amount, payment_method=payment.payment_method, status=payment.status, transaction_reference=payment.transaction_reference)

@router.post("/{order_id}/payment", response_model=PaymentResponse)
def pay(order_id: int, data: PaymentRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    payment, _ = PaymentService(db, OrderRepository(db), PaymentRepository(db), TokenRepository(db), DummyUPIGateway()).pay(order_id, user.id, data)
    return response(payment)

@router.get("/{order_id}/payment", response_model=PaymentResponse)
def payment(order_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return response(PaymentService(db, OrderRepository(db), PaymentRepository(db), TokenRepository(db), DummyUPIGateway()).get_for_student(order_id, user.id))
