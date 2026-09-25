import React, { useEffect, useMemo, useState } from 'react';
import { ChefHat, History, LogOut, Minus, Plus, Search, ShoppingCart, UtensilsCrossed, XCircle } from 'lucide-react';
import { StatusBadge } from '../../components/Badge';

const API_URL = 'http://127.0.0.1:8000';

export function StudentPortal({ user, onLogout }) {
  const [menu, setMenu] = useState([]);
  const [orders, setOrders] = useState([]);
  const [cart, setCart] = useState({});
  const [activeTab, setActiveTab] = useState('menu');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [cancellingId, setCancellingId] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [availableOnly, setAvailableOnly] = useState(false);
  const [sortBy, setSortBy] = useState('default');

  const request = async (path, options = {}) => {
    const token = localStorage.getItem('canteen_student_token');
    const response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers },
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || 'Request failed');
    return data;
  };

  const load = async () => {
    setLoading(true);
    try {
      const [items, studentOrders] = await Promise.all([request('/api/menu'), request('/api/orders')]);
      setMenu(items);
      setOrders(studentOrders);
    } catch (error) { setMessage(error.message); } finally { setLoading(false); }
  };

  const categories = useMemo(() => {
    const cats = new Set(menu.map((i) => i.category).filter(Boolean));
    return ['All', ...Array.from(cats)];
  }, [menu]);

  const filteredMenu = useMemo(() => {
    return menu
      .filter((item) => {
        if (selectedCategory !== 'All' && item.category?.toLowerCase() !== selectedCategory.toLowerCase()) {
          return false;
        }
        if (availableOnly && !item.is_available) {
          return false;
        }
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase();
          const nameMatch = item.name?.toLowerCase().includes(q);
          const descMatch = (item.description || '').toLowerCase().includes(q);
          if (!nameMatch && !descMatch) return false;
        }
        return true;
      })
      .sort((a, b) => {
        if (sortBy === 'price-asc') return Number(a.price) - Number(b.price);
        if (sortBy === 'price-desc') return Number(b.price) - Number(a.price);
        if (sortBy === 'name') return (a.name || '').localeCompare(b.name || '');
        return 0;
      });
  }, [menu, selectedCategory, availableOnly, searchQuery, sortBy]);

  useEffect(() => { load(); }, []);

  const cartItems = useMemo(
    () => menu.filter((item) => cart[item.id]).map((item) => ({ ...item, quantity: cart[item.id] })),
    [menu, cart],
  );
  const total = cartItems.reduce((sum, item) => sum + Number(item.price) * item.quantity, 0);
  const quantity = cartItems.reduce((sum, item) => sum + item.quantity, 0);

  const changeQuantity = (item, change) => setCart((previous) => {
    const next = { ...previous };
    const nextQuantity = (next[item.id] || 0) + change;
    if (nextQuantity <= 0) delete next[item.id]; else next[item.id] = nextQuantity;
    return next;
  });

  const placeOrder = async () => {
    if (!cartItems.length) return;
    try {
      const order = await request('/api/orders', {
        method: 'POST',
        body: JSON.stringify({ items: cartItems.map((item) => ({ menu_item_id: item.id, quantity: item.quantity })) }),
      });
      setCart({});
      setMessage(`Order #${order.id} placed successfully.`);
      setActiveTab('orders');
      await load();
    } catch (error) { setMessage(error.message); }
  };

  const cancelOrder = async (orderId) => {
    setCancellingId(orderId);
    try {
      const updatedOrder = await request(`/api/orders/${orderId}/cancel`, { method: 'POST' });
      setOrders((previous) => previous.map((order) => (order.id === orderId ? updatedOrder : order)));
      setMessage(`Order #${orderId} cancelled.`);
      await load();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setCancellingId(null);
    }
  };

const menuView = (
    <div>
      {/* Search and Category Bar */}
      <div className="filter-bar" style={{ marginBottom: '1rem' }}>
        <div className="search-input-wrap">
          <Search size={16} />
          <input
            type="text"
            className="search-input"
            placeholder="Search food by name or description..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="filter-group">
          {categories.map((cat) => (
            <button
              key={cat}
              type="button"
              className={`filter-chip ${selectedCategory === cat ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat)}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Sub-toolbar: Available only toggle & Sort selector */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '1.25rem' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', userSelect: 'none', fontSize: '0.875rem' }}>
          <input
            type="checkbox"
            checked={availableOnly}
            onChange={(e) => setAvailableOnly(e.target.checked)}
            style={{ cursor: 'pointer' }}
          />
          <span>Show available only</span>
        </label>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}>
          <span style={{ color: 'var(--color-text-muted)' }}>Sort by:</span>
          <select
            className="form-control"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            style={{ padding: '0.25rem 0.6rem', fontSize: '0.85rem', width: 'auto' }}
          >
            <option value="default">Default</option>
            <option value="price-asc">Price: Low to High</option>
            <option value="price-desc">Price: High to Low</option>
            <option value="name">Name (A–Z)</option>
          </select>
        </div>
      </div>

      {/* Dishes Grid or Empty State */}
      {filteredMenu.length === 0 ? (
        <div className="card-container">
          <div className="state-box">
            <UtensilsCrossed />
            <h4>No food items found</h4>
            <p>
              {searchQuery
                ? `No items match "${searchQuery}"`
                : selectedCategory !== 'All'
                ? `No items available in "${selectedCategory}"`
                : 'No dishes match your selected filters.'}
            </p>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => {
                setSearchQuery('');
                setSelectedCategory('All');
                setAvailableOnly(false);
                setSortBy('default');
              }}
              style={{ marginTop: '0.5rem' }}
            >
              Clear filters
            </button>
          </div>
        </div>
      ) : (
        <div className="metrics-grid">
          {filteredMenu.map((item) => (
            <div
              className="metric-card"
              key={item.id}
              style={{ alignItems: 'flex-start', opacity: item.is_available ? 1 : 0.55 }}
            >
              <div className="metric-data" style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                  <div className="metric-value" style={{ fontSize: '1.1rem' }}>{item.name}</div>
                  <span
                    style={{
                      padding: '0.15rem 0.5rem',
                      borderRadius: 'var(--radius-full)',
                      background: 'rgba(255, 255, 255, 0.08)',
                      fontSize: '0.72rem',
                      color: 'var(--color-text-muted)',
                    }}
                  >
                    {item.category}
                  </span>
                </div>
                <p className="customer-sub">{item.description}</p>
                <p style={{ color: 'var(--color-primary)', marginTop: '.5rem', fontWeight: 700 }}>
                  ₹{Number(item.price).toFixed(2)}
                </p>
              </div>
              {item.is_available ? (
                <div className="order-actions">
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => changeQuantity(item, -1)}
                    disabled={!cart[item.id]}
                  >
                    <Minus size={15} />
                  </button>
                  <span style={{ minWidth: '1.25rem', textAlign: 'center' }}>
                    {cart[item.id] || 0}
                  </span>
                  <button
                    className="btn btn-primary btn-sm"
                    onClick={() => changeQuantity(item, 1)}
                  >
                    <Plus size={15} />
                  </button>
                </div>
              ) : (
                <span className="badge badge-cancelled">Unavailable</span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
  const cartView = <section className="card-container" style={{ padding: '1.25rem' }}>{cartItems.length ? <><div className="page-header"><div className="page-title"><h2>Your cart</h2><p>Review quantities before placing your order.</p></div><button className="btn btn-primary" onClick={placeOrder}>Place order · ₹{total.toFixed(2)}</button></div>{cartItems.map((item) => <div className="order-item-row" style={{ padding: '.85rem 0', borderBottom: '1px solid var(--color-border)' }} key={item.id}><div><strong>{item.name}</strong><div className="customer-sub">₹{Number(item.price).toFixed(2)} each</div></div><div className="order-actions"><button className="btn btn-secondary btn-sm" onClick={() => changeQuantity(item, -1)}><Minus size={15} /></button><span>{item.quantity}</span><button className="btn btn-primary btn-sm" onClick={() => changeQuantity(item, 1)}><Plus size={15} /></button><strong style={{ minWidth: '5rem', textAlign: 'right' }}>₹{(Number(item.price) * item.quantity).toFixed(2)}</strong></div></div>)}<div className="order-footer"><strong>Total</strong><strong className="order-total-val">₹{total.toFixed(2)}</strong></div></> : <div className="state-box"><ShoppingCart /><h4>Your cart is empty</h4><button className="btn btn-primary" onClick={() => setActiveTab('menu')}>Browse menu</button></div>}</section>;

  const ordersView = <div className="orders-grid">{orders.length ? orders.map((order) => { const canCancel = order.status === 'PLACED'; return <div className="order-card" key={order.id}><div className="order-card-header"><strong>Order #{order.id}</strong><StatusBadge status={order.status} /></div>{order.items.map((item) => <div className="order-item-row" key={item.id}><span>{item.quantity}× item #{item.menu_item_id}</span><span>₹{Number(item.subtotal).toFixed(2)}</span></div>)}<div className="order-footer"><strong>Total: ₹{Number(order.total_amount).toFixed(2)}</strong>{canCancel && <button className="btn btn-secondary btn-sm" onClick={() => cancelOrder(order.id)} disabled={cancellingId === order.id}><XCircle size={15} />{cancellingId === order.id ? 'Cancelling...' : 'Cancel Order'}</button>}</div></div>; }) : <div className="state-box"><History /><h4>No orders yet</h4><button className="btn btn-primary" onClick={() => setActiveTab('menu')}>Order something</button></div>}</div>;

  const tabs = [{ id: 'menu', label: 'Menu', icon: UtensilsCrossed }, { id: 'cart', label: `View Cart (${quantity})`, icon: ShoppingCart }, { id: 'orders', label: 'Order History', icon: History }];
  const content = activeTab === 'menu' ? menuView : activeTab === 'cart' ? cartView : ordersView;

  return <div className="app-container"><nav className="navbar"><div className="navbar-inner"><div className="brand"><div className="brand-icon"><ChefHat size={22} /></div><div className="brand-text"><h1>Smart Canteen</h1><span>Student ordering</span></div></div><div className="nav-links">{tabs.map((tab) => { const Icon = tab.icon; return <button key={tab.id} className={`nav-item ${activeTab === tab.id ? 'active' : ''}`} onClick={() => setActiveTab(tab.id)}><Icon size={16} />{tab.label}</button>; })}</div><div className="nav-user"><span className="user-name">{user.name}</span><button className="btn-logout" onClick={onLogout}><LogOut size={16} />Logout</button></div></div></nav><main className="main-content"><div className="page-header"><div className="page-title"><h2>{activeTab === 'menu' ? 'Today’s Menu' : activeTab === 'cart' ? 'Your Cart' : 'Order History'}</h2><p>{activeTab === 'menu' ? 'Add available dishes to your cart.' : activeTab === 'cart' ? 'Review and place your order.' : 'Track orders placed from this account.'}</p></div><button className="btn btn-secondary" onClick={load}>Refresh</button></div>{message && <div className="toast toast-info" style={{ position: 'static', marginBottom: '1rem' }}>{message}</div>}{loading ? <div className="state-box"><div className="spinner" /><p>Loading…</p></div> : content}</main></div>;
}
