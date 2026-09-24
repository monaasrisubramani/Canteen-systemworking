import secrets
from datetime import UTC, datetime
from sqlalchemy.orm import Session
from app.core.exceptions import AppError
from app.models.digital_token import DigitalToken
from app.models.enums import OrderStatus, PaymentStatus, TokenStatus
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.token_repository import TokenRepository

class TokenService:
    def __init__(self, session: Session, tokens: TokenRepository, orders: OrderRepository, payments: PaymentRepository):
        self.session, self.tokens, self.orders, self.payments = session, tokens, orders, payments
    def create_for_paid_order(self, order_id: int) -> DigitalToken:
        if self.tokens.get_for_order(order_id): raise AppError("Digital token already exists", 409)
        if not self.payments.has_successful_payment(order_id): raise AppError("A successful payment is required", 409)
        for _ in range(5):
            code = f"CANT-{secrets.token_hex(3).upper()}"
            if not self.tokens.get_by_code(code): return self.tokens.create(DigitalToken(order_id=order_id, token_code=code, status=TokenStatus.ACTIVE))
        raise AppError("Unable to generate a unique digital token", 500)
    def get_for_student(self, order_id: int, user_id: int) -> DigitalToken:
        order = self.orders.get_by_id(order_id)
        if not order: raise AppError("Order not found", 404)
        if order.user_id != user_id: raise AppError("Forbidden", 403)
        token = self.tokens.get_for_order(order_id)
        if not token: raise AppError("Digital token not found", 404)
        return token
    def verify(self, code: str) -> DigitalToken:
        token = self.tokens.get_by_code(code.upper())
        if not token: raise AppError("Token not found", 404)
        return token
    def redeem(self, code: str) -> DigitalToken:
        token = self.verify(code)
        if token.status == TokenStatus.REDEEMED: raise AppError("Token already redeemed", 409)
        if token.status != TokenStatus.ACTIVE: raise AppError("Token cannot be redeemed", 409)
        order = self.orders.get_by_id(token.order_id)
        if not self.payments.has_successful_payment(order.id): raise AppError("Token payment is not successful", 409)
        if order.status != OrderStatus.READY: raise AppError("Order must be READY before collection", 409)
        token.status = TokenStatus.REDEEMED
        token.redeemed_at = datetime.now(UTC)
        order.status = OrderStatus.COLLECTED
        return token
