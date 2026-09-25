from decimal import Decimal
from pydantic import BaseModel, Field

class PaymentRequest(BaseModel):
    payment_method: str = Field(default="UPI")
    upi_id: str = Field(min_length=3, max_length=255)
    upi_app: str | None = Field(default=None)

class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    payment_method: str
    status: str
    transaction_reference: str | None = None
    token_code: str | None = None
