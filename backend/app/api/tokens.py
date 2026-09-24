from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, get_db, require_admin
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.token_repository import TokenRepository
from app.schemas.token import TokenResponse, TokenVerificationResponse
from app.services.token_service import TokenService

router = APIRouter(tags=["Digital Tokens"])

def service(db): return TokenService(db, TokenRepository(db), OrderRepository(db), PaymentRepository(db))
def token_response(token): return TokenResponse(order_id=token.order_id, token_code=token.token_code, status=token.status, redeemed_at=token.redeemed_at)

@router.get("/api/orders/{order_id}/token", response_model=TokenResponse)
def get_token(order_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)): return token_response(service(db).get_for_student(order_id, user.id))

@router.get("/api/admin/tokens/{token_code}", response_model=TokenVerificationResponse)
def verify_token(token_code: str, _: object = Depends(require_admin), db: Session = Depends(get_db)):
    token = service(db).verify(token_code); order = OrderRepository(db).get_by_id(token.order_id); payment = PaymentRepository(db).list_for_order(order.id)[-1]
    return TokenVerificationResponse(token_code=token.token_code, token_status=token.status, order_id=order.id, order_status=order.status, payment_status=payment.status)

@router.post("/api/tokens/{token_code}/redeem", response_model=TokenResponse)
def redeem_token(token_code: str, _: object = Depends(require_admin), db: Session = Depends(get_db)): return token_response(service(db).redeem(token_code))
