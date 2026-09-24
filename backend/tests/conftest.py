import pytest
from fastapi.testclient import TestClient
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db
from app.main import app
from app.models.enums import UserRole
from app.models.menu_item import MenuItem
from app.db.base import Base
from app.models.user import User

# Single in-memory SQLite shared pool across threads/sessions in testing
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=test_engine)
    with TestingSessionLocal() as session:
        session.add_all(
            [
                User(name="Demo Student", email="student@example.com", password_hash="prototype-password", role=UserRole.STUDENT),
                User(name="Canteen Admin", email="admin@example.com", password_hash="prototype-password", role=UserRole.ADMIN),
                User(name="Regular Student", email="student1@example.com", password_hash="student123", role=UserRole.STUDENT),
            ]
        )
        session.add_all(
            [
                MenuItem(name="Idli", description="Steamed rice cakes with chutney.", price=Decimal("35.00"), category="Breakfast", is_available=True),
                MenuItem(name="Dosa", description="Crisp dosa with sambar.", price=Decimal("50.00"), category="Breakfast", is_available=True),
                MenuItem(name="Veg Meals", description="Rice, vegetables and dal.", price=Decimal("40.00"), category="Meals", is_available=True),
                MenuItem(name="Lemon Rice", description="Tangy lemon rice.", price=Decimal("35.00"), category="Meals", is_available=True),
            ]
        )
        session.flush()
        session.commit()
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def admin_token(client):
    res = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "prototype-password"})
    return res.json()["access_token"]
