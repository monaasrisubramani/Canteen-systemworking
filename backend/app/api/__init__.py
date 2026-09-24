"""HTTP route modules."""

from app.api.auth import router as auth_router
from app.api.menu import router as menu_router
from app.api.orders import router as orders_router

__all__ = ["auth_router", "menu_router", "orders_router"]
