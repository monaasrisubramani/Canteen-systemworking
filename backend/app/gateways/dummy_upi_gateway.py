import secrets
from decimal import Decimal
from app.gateways.payment_gateway import GatewayResult

class DummyUPIGateway:
    """Prototype simulator. `fail@upi` deliberately returns FAILED; no real money moves."""
    def charge_upi(self, order_id: int, amount: Decimal, upi_id: str) -> GatewayResult:
        if upi_id.lower().startswith("fail@"):
            return GatewayResult(success=False)
        return GatewayResult(success=True, transaction_reference=f"UPI-TXN-{order_id}-{secrets.token_hex(3).upper()}")
