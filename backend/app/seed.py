"""Run after migrations: python -m app.seed"""
from decimal import Decimal
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.digital_token import DigitalToken
from app.models.enums import OrderStatus, PaymentMethod, PaymentStatus, TokenStatus, UserRole
from app.models.menu_item import MenuItem
from app.models.order import Order, OrderItem
from app.models.payment import Payment
from app.models.user import User

MENU = [("Idli", "Steamed rice cakes with chutney.", "35", "Breakfast", True), ("Dosa", "Crisp dosa with sambar.", "50", "Breakfast", True), ("Veg Meals", "Rice, vegetables and dal.", "40", "Meals", True), ("Chicken Rice", "Chicken rice.", "90", "Meals", False), ("Lemon Rice", "Tangy lemon rice.", "35", "Meals", True), ("Samosa", "Vegetable samosa.", "15", "Snacks", True), ("Tea", "Fresh tea.", "15", "Beverages", True), ("Coffee", "Filter coffee.", "20", "Beverages", True), ("Juice", "Seasonal fruit juice.", "30", "Beverages", False)]

def seed():
    with SessionLocal() as session:
        if session.scalar(select(User.id).limit(1)):
            print("Seed skipped: database already contains users."); return
        session.add_all([User(name="Demo Student", email="student@example.com", password_hash="prototype-password", role=UserRole.STUDENT), User(name="Canteen Admin", email="admin@example.com", password_hash="prototype-password", role=UserRole.ADMIN)])
        session.add_all([MenuItem(name=name, description=description, price=Decimal(price), category=category, is_available=available) for name, description, price, category, available in MENU])
        session.flush()
        student = session.scalar(select(User).where(User.email == "student@example.com"))
        items = list(session.scalars(select(MenuItem).order_by(MenuItem.id)))
        scenarios = [(OrderStatus.PLACED, PaymentStatus.PENDING, None), (OrderStatus.PREPARING, PaymentStatus.FAILED, None), (OrderStatus.READY, PaymentStatus.SUCCESS, TokenStatus.ACTIVE), (OrderStatus.COLLECTED, PaymentStatus.SUCCESS, TokenStatus.REDEEMED)]
        for index, (status, payment_status, token_status) in enumerate(scenarios):
            item = items[index]
            order = Order(user=student, total_amount=item.price, status=status)
            order.items.append(OrderItem(menu_item=item, quantity=1, unit_price=item.price, subtotal=item.price))
            session.add(order); session.flush()
            session.add(Payment(order=order, amount=item.price, payment_method=PaymentMethod.UPI, status=payment_status, transaction_reference=f"UPI-SEED-{order.id}" if payment_status == PaymentStatus.SUCCESS else None, upi_id="student@upi"))
            if token_status: session.add(DigitalToken(order=order, token_code=f"CANT-SEED-{order.id}", status=token_status))
        session.commit(); print("Seed completed: users, menu, orders, payments, and tokens created.")

if __name__ == "__main__": seed()
