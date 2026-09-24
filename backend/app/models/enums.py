from enum import StrEnum

class UserRole(StrEnum): STUDENT = "STUDENT"; ADMIN = "ADMIN"
class OrderStatus(StrEnum): PLACED = "PLACED"; PREPARING = "PREPARING"; READY = "READY"; COLLECTED = "COLLECTED"; CANCELLED = "CANCELLED"
class PaymentMethod(StrEnum): UPI = "UPI"
class PaymentStatus(StrEnum): PENDING = "PENDING"; SUCCESS = "SUCCESS"; FAILED = "FAILED"
class TokenStatus(StrEnum): ACTIVE = "ACTIVE"; REDEEMED = "REDEEMED"; CANCELLED = "CANCELLED"
