from datetime import datetime
from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import TokenStatus

class DigitalToken(Base):
    __tablename__ = "digital_tokens"
    __table_args__ = (UniqueConstraint("order_id", name="uq_digital_tokens_order_id"), UniqueConstraint("token_code", name="uq_digital_tokens_token_code"))
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    token_code: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    status: Mapped[TokenStatus] = mapped_column(Enum(TokenStatus), default=TokenStatus.ACTIVE, index=True, nullable=False)
    redeemed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    order: Mapped["Order"] = relationship(back_populates="token")
