import re
from sqlalchemy.orm import Session
from app.core.exceptions import AppError
from app.gateways.payment_gateway import PaymentGateway
from app.models.enums import PaymentMethod, PaymentStatus
from app.models.payment import Payment
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.token_repository import TokenRepository
from app.schemas.payment import PaymentRequest
from app.services.token_service import TokenService

class PaymentService:
    def __init__(self, session: Session, orders: OrderRepository, payments: PaymentRepository, tokens: TokenRepository, gateway: PaymentGateway):
        self.session, self.orders, self.payments, self.tokens, self.gateway = session, orders, payments, tokens, gateway
    def pay(self, order_id: int, user_id: int, request: PaymentRequest):
        order = self.orders.get_by_id(order_id)
        if not order: raise AppError("Order not found", 404)
        if order.user_id != user_id: raise AppError("Forbidden", 403)
        if self.payments.has_successful_payment(order_id): raise AppError("Order already paid", 409)
        if request.payment_method.upper() != PaymentMethod.UPI: raise AppError("Only UPI payment is supported", 422)
        upi_id = request.upi_id.strip().lower()
        if not re.fullmatch(r"[a-z0-9._-]+@[a-z0-9._-]+", upi_id): raise AppError("Invalid UPI ID", 422)
        result = self.gateway.charge_upi(order.id, order.total_amount, upi_id)
        payment = self.payments.create(Payment(order_id=order.id, amount=order.total_amount, payment_method=PaymentMethod.UPI, status=PaymentStatus.SUCCESS if result.success else PaymentStatus.FAILED, transaction_reference=result.transaction_reference, upi_id=upi_id))
        token = None
        if result.success: token = TokenService(self.session, self.tokens, self.orders, self.payments).create_for_paid_order(order.id)
        return payment, token
    def get_for_student(self, order_id: int, user_id: int):
        order = self.orders.get_by_id(order_id)
        if not order: raise AppError("Order not found", 404)
        if order.user_id != user_id: raise AppError("Forbidden", 403)
        payments = self.payments.list_for_order(order_id)
        if not payments: raise AppError("Payment not found", 404)
        return payments[-1]
