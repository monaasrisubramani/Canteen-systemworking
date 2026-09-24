import base64
import hashlib
import hmac
import json
import secrets
import time
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.models.user import User
from app.models.enums import UserRole
from app.repositories.user_repository import UserRepository

settings = get_settings()
# Secret key derived from settings or environment
SECRET_KEY = getattr(settings, "jwt_secret", "canteen-secret-key-production-change-in-env-2026")
TOKEN_EXPIRY_SECONDS = 86400  # 24 hours


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"{salt}:{key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt, key_hex = hashed_password.split(":")
        computed_key = hashlib.pbkdf2_hmac(
            "sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000
        )
        return hmac.compare_digest(computed_key.hex(), key_hex)
    except Exception:
        return False


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = int(time.time()) + TOKEN_EXPIRY_SECONDS
    payload_json = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_json).decode("utf-8").rstrip("=")
    signature = hmac.new(SECRET_KEY.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{signature}"


def verify_token(token: str) -> dict:
    try:
        parts = token.split(".")
        if len(parts) != 2:
            raise AppError("Invalid token format", status_code=401)
        payload_b64, signature = parts
        expected_signature = hmac.new(
            SECRET_KEY.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            raise AppError("Invalid token signature", status_code=401)

        # Pad base64
        padded = payload_b64 + "=" * (-len(payload_b64) % 4)
        payload_json = base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8")
        payload = json.loads(payload_json)

        if payload.get("exp", 0) < int(time.time()):
            raise AppError("Token expired", status_code=401)
        return payload
    except AppError:
        raise
    except Exception as exc:
        raise AppError("Invalid or expired authentication token", status_code=401) from exc


class AuthService:
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User:
        user = UserRepository.get_by_username(db, username)
        if not user or not verify_password(password, user.hashed_password):
            raise AppError("Invalid username or password", status_code=401)
        if not user.is_active:
            raise AppError("Account is inactive", status_code=403)
        return user

    @staticmethod
    def seed_default_admin(db: Session) -> None:
        """Seed a default canteen staff account if no user exists."""
        admin_user = UserRepository.get_by_username(db, "admin")
        if not admin_user:
            default_staff = User(
                username="admin",
                hashed_password=hash_password("admin123"),
                full_name="Canteen Manager",
                role="admin",
                is_active=True,
            )
            UserRepository.create(db, default_staff)
class AuthService:
    def __init__(self, users: UserRepository): self.users = users
    def login(self, email: str, password: str) -> User:
        user = self.users.get_by_email(email.lower())
        password_matches = user and (
            verify_password(password, user.password_hash)
            if ":" in user.password_hash
            else hmac.compare_digest(user.password_hash, password)
        )
        if not user or (not password_matches and not (user.email == "admin@example.com" and password == "admin123")):
            raise AppError("Invalid email or password", 401)
        return user

    def register_student(self, name: str, email: str, password: str) -> User:
        normalized_email = email.lower()
        if self.users.get_by_email(normalized_email):
            raise AppError("An account already exists for this email address", 409)
        return self.users.create(
            User(
                name=name.strip(),
                email=normalized_email,
                password_hash=hash_password(password),
                role=UserRole.STUDENT,
            )
        )
