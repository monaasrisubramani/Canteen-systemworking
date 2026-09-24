from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.enums import PaymentStatus
from app.models.payment import Payment

class PaymentRepository:
    def __init__(self, session: Session): self.session = session
    def list_for_order(self, order_id: int): return list(self.session.scalars(select(Payment).where(Payment.order_id == order_id)))
    def has_successful_payment(self, order_id: int): return self.session.scalar(select(Payment.id).where(Payment.order_id == order_id, Payment.status == PaymentStatus.SUCCESS)) is not None
    def create(self, payment: Payment): self.session.add(payment); self.session.flush(); return payment
