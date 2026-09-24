"""Initial canteen schema."""
from alembic import op
import sqlalchemy as sa

revision = "20260910_0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    role = sa.Enum("STUDENT", "ADMIN", name="userrole")
    order_status = sa.Enum("PLACED", "PREPARING", "READY", "COLLECTED", "CANCELLED", name="orderstatus")
    method = sa.Enum("UPI", name="paymentmethod")
    payment_status = sa.Enum("PENDING", "SUCCESS", "FAILED", name="paymentstatus")
    token_status = sa.Enum("ACTIVE", "REDEEMED", "CANCELLED", name="tokenstatus")
    def timestamps(): return [sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False)]
    op.create_table("users", sa.Column("id", sa.Integer, primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("email", sa.String(255), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("role", role, nullable=False), *timestamps())
    op.create_index("ix_users_email", "users", ["email"], unique=True); op.create_index("ix_users_role", "users", ["role"])
    op.create_table("menu_items", sa.Column("id", sa.Integer, primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("description", sa.Text, nullable=False), sa.Column("price", sa.Numeric(10,2), nullable=False), sa.Column("category", sa.String(80), nullable=False), sa.Column("is_available", sa.Boolean, nullable=False), *timestamps())
    op.create_index("ix_menu_items_name", "menu_items", ["name"], unique=True); op.create_index("ix_menu_items_category", "menu_items", ["category"]); op.create_index("ix_menu_items_is_available", "menu_items", ["is_available"])
    op.create_table("orders", sa.Column("id", sa.Integer, primary_key=True), sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False), sa.Column("total_amount", sa.Numeric(10,2), nullable=False), sa.Column("status", order_status, nullable=False), *timestamps())
    op.create_index("ix_orders_user_id", "orders", ["user_id"]); op.create_index("ix_orders_status", "orders", ["status"])
    op.create_table("order_items", sa.Column("id", sa.Integer, primary_key=True), sa.Column("order_id", sa.Integer, sa.ForeignKey("orders.id"), nullable=False), sa.Column("menu_item_id", sa.Integer, sa.ForeignKey("menu_items.id"), nullable=False), sa.Column("quantity", sa.Integer, nullable=False), sa.Column("unit_price", sa.Numeric(10,2), nullable=False), sa.Column("subtotal", sa.Numeric(10,2), nullable=False))
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"]); op.create_index("ix_order_items_menu_item_id", "order_items", ["menu_item_id"])
    op.create_table("payments", sa.Column("id", sa.Integer, primary_key=True), sa.Column("order_id", sa.Integer, sa.ForeignKey("orders.id"), nullable=False), sa.Column("amount", sa.Numeric(10,2), nullable=False), sa.Column("payment_method", method, nullable=False), sa.Column("status", payment_status, nullable=False), sa.Column("transaction_reference", sa.String(100)), sa.Column("upi_id", sa.String(255), nullable=False), *timestamps(), sa.UniqueConstraint("transaction_reference", name="uq_payments_transaction_reference"))
    op.create_index("ix_payments_order_id", "payments", ["order_id"]); op.create_index("ix_payments_status", "payments", ["status"])
    op.create_table("digital_tokens", sa.Column("id", sa.Integer, primary_key=True), sa.Column("order_id", sa.Integer, sa.ForeignKey("orders.id"), nullable=False), sa.Column("token_code", sa.String(32), nullable=False), sa.Column("status", token_status, nullable=False), sa.Column("redeemed_at", sa.DateTime(timezone=True)), *timestamps(), sa.UniqueConstraint("order_id", name="uq_digital_tokens_order_id"), sa.UniqueConstraint("token_code", name="uq_digital_tokens_token_code"))
    op.create_index("ix_digital_tokens_token_code", "digital_tokens", ["token_code"]); op.create_index("ix_digital_tokens_status", "digital_tokens", ["status"])

def downgrade():
    op.drop_table("digital_tokens"); op.drop_table("payments"); op.drop_table("order_items"); op.drop_table("orders"); op.drop_table("menu_items"); op.drop_table("users")
