from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User | None:
        return db.get(User, user_id)

    @staticmethod
    def get_by_username(db: Session, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return db.scalars(stmt).first()

    @staticmethod
    def create(db: Session, user: User) -> User:
        db.add(user)
        db.flush()
        db.refresh(user)
        return user
from app.models.user import User

class UserRepository:
    def __init__(self, session: Session): self.session = session
    def get_by_id(self, user_id: int): return self.session.get(User, user_id)
    def get_by_email(self, email: str): return self.session.scalar(select(User).where(User.email == email))
    def create(self, user: User): self.session.add(user); self.session.flush(); return user
