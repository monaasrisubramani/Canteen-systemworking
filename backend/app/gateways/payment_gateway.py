from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

@dataclass(frozen=True)
class GatewayResult:
    success: bool
    transaction_reference: str | None = None

class PaymentGateway(Protocol):
    def charge_upi(self, order_id: int, amount: Decimal, upi_id: str) -> GatewayResult: ...
