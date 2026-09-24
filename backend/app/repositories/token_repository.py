from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.digital_token import DigitalToken

class TokenRepository:
    def __init__(self, session: Session): self.session = session
    def get_by_code(self, code: str): return self.session.scalar(select(DigitalToken).where(DigitalToken.token_code == code))
    def get_for_order(self, order_id: int): return self.session.scalar(select(DigitalToken).where(DigitalToken.order_id == order_id))
    def create(self, token: DigitalToken): self.session.add(token); self.session.flush(); return token
