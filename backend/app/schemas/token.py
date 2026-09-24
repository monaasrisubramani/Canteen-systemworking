from datetime import datetime
from pydantic import BaseModel

class TokenResponse(BaseModel):
    order_id: int
    token_code: str
    status: str
    redeemed_at: datetime | None

class TokenVerificationResponse(BaseModel):
    token_code: str
    token_status: str
    order_id: int
    order_status: str
    payment_status: str
