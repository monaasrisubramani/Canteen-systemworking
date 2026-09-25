import React, { useEffect, useState, useCallback } from 'react';
import {
  ClipboardList,
  Search,
  RefreshCw,
  Clock,
  ChefHat,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Phone,
  User,
  Calendar,
  Ticket,
} from 'lucide-react';
import { AdminAPI } from '../../api/admin';
import { StatusBadge, PaymentBadge } from '../../components/Badge';

export function OrderManagement({ onShowToast }) {
  const [orders, setOrders] = useState([]);
  const [selectedStatus, setSelectedStatus] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState(null);
  const [error, setError] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(true);

  const statusFilters = [
    { label: 'All', value: 'All' },
    { label: 'Placed', value: 'PLACED' },
    { label: 'Preparing', value: 'PREPARING' },
    { label: 'Ready', value: 'READY' },
    { label: 'Collected', value: 'COLLECTED' },
    { label: 'Cancelled', value: 'CANCELLED' },
  ];

  const fetchOrders = useCallback(async (quiet = false) => {
    if (!quiet) setLoading(true);
    setError('');
    try {
      const data = await AdminAPI.getOrders(selectedStatus);
      setOrders(data || []);
    } catch (err) {
      setError(err.message || 'Failed to load incoming orders');
    } finally {
      if (!quiet) setLoading(false);
    }
  }, [selectedStatus]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  // Auto-refresh every 12 seconds when enabled
  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      fetchOrders(true);
    }, 12000);
    return () => clearInterval(interval);
  }, [autoRefresh, fetchOrders]);

  const handleUpdateStatus = async (orderId, newStatus) => {
    setUpdatingId(orderId);
    try {
      const updated = await AdminAPI.updateOrderStatus(orderId, newStatus);
      setOrders((prev) =>
        prev.map((o) => (o.id === orderId ? { ...o, status: updated.status } : o))
      );
      if (onShowToast) {
        onShowToast(`Order #${orderId} transitioned to ${newStatus}`, 'success');
      }
    } catch (err) {
      if (onShowToast) {
        onShowToast(err.message || `Failed to update Order #${orderId}`, 'error');
      }
    } finally {
      setUpdatingId(null);
    }
  };

  const filteredOrders = orders.filter((order) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    const idMatch = String(order.id).includes(q);
    const customerMatch = (order.customer_name || '').toLowerCase().includes(q);
    const tokenMatch = (order.token_code || '').toLowerCase().includes(q);
    const itemMatch = (order.items || []).some((item) =>
      (item.item_name || '').toLowerCase().includes(q)
    );
    return idMatch || customerMatch || tokenMatch || itemMatch;
  });

  const formatTime = (isoString) => {
    if (!isoString) return '';
    try {
      const d = new Date(isoString);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  const formatDate = (isoString) => {
    if (!isoString) return '';
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
    } catch {
      return '';
    }
  };

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          <h2>Incoming Orders</h2>
          <p>Process, monitor, and transition order workflow in real-time</p>
        </div>
        <div className="page-actions">
          <label
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              fontSize: '0.85rem',
              color: 'var(--color-text-muted)',
              cursor: 'pointer',
              userSelect: 'none',
              marginRight: '0.5rem',
            }}
          >
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              style={{ cursor: 'pointer' }}
            />
            <span>Auto-refresh</span>
          </label>

          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => fetchOrders(false)}
            disabled={loading}
          >
            <RefreshCw size={15} className={loading ? 'spinner' : ''} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {error && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.6rem',
            padding: '0.9rem 1.25rem',
            borderRadius: 'var(--radius-md)',
            background: 'var(--color-danger-bg)',
            border: '1px solid var(--color-danger)',
            color: 'var(--color-danger)',
            marginBottom: '1.5rem',
          }}
        >
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="filter-bar">
        <div className="search-input-wrap">
          <Search size={16} />
          <input
            type="text"
            className="search-input"
            placeholder="Search by Order ID, customer, token code, item..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="filter-group">
          {statusFilters.map((s) => (
            <button
              key={s.value}
              type="button"
              className={`filter-chip ${selectedStatus === s.value ? 'active' : ''}`}
              onClick={() => setSelectedStatus(s.value)}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* Orders View */}
      {loading ? (
        <div className="state-box">
          <div className="spinner"></div>
          <p>Loading incoming orders...</p>
        </div>
      ) : filteredOrders.length === 0 ? (
        <div className="card-container">
          <div className="state-box">
            <ClipboardList />
            <h4>No orders found</h4>
            <p>
              {searchQuery
                ? `No orders match query "${searchQuery}"`
                : selectedStatus !== 'All'
                ? `No orders currently in "${selectedStatus}" status`
                : 'The kitchen is all caught up! New orders will arrive here.'}
            </p>
          </div>
        </div>
      ) : (
        <div className="orders-grid">
          {filteredOrders.map((order) => {
            const isUpdating = updatingId === order.id;
            const normStatus = (order.status || '').toUpperCase();

            return (
              <div
                key={order.id}
                className="order-card"
                style={{
                  borderLeft:
                    normStatus === 'PLACED' || normStatus === 'PENDING'
                      ? '4px solid #f59e0b'
                      : normStatus === 'PREPARING'
                      ? '4px solid #06b6d4'
                      : normStatus === 'READY'
                      ? '4px solid #a855f7'
                      : normStatus === 'COLLECTED' || normStatus === 'COMPLETED'
                      ? '4px solid #10b981'
                      : '1px solid var(--color-border)',
                }}
              >
                <div className="order-card-header">
                  <div className="order-id-block">
                    <div className="order-number">Order #{order.id}</div>
                    <div className="order-time" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <Calendar size={12} />
                      <span>{formatDate(order.created_at)} at {formatTime(order.created_at)}</span>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', flexWrap: 'wrap' }}>
                    {order.payment_status && <PaymentBadge status={order.payment_status} />}
                    <StatusBadge status={order.status} />
                  </div>
                </div>

                <div className="order-customer">
                  <div className="customer-name" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <User size={14} color="var(--color-text-dim)" />
                    <span>{order.customer_name}</span>
                  </div>
                  {order.token_code && (
                    <div style={{ marginTop: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <span
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.3rem',
                          padding: '0.15rem 0.5rem',
                          borderRadius: 4,
                          background: 'rgba(168, 85, 247, 0.15)',
                          color: '#c084fc',
                          fontSize: '0.78rem',
                          fontWeight: 600,
                        }}
                      >
                        <Ticket size={12} />
                        Token: {order.token_code}
                      </span>
                    </div>
                  )}
                  {order.customer_email && (
                    <div className="customer-sub" style={{ paddingLeft: '1.25rem', fontSize: '0.78rem' }}>
                      {order.customer_email}
                    </div>
                  )}
                </div>

                <div className="order-items-list">
                  {(order.items || []).map((item, idx) => {
                    const linePrice = item.subtotal != null
                      ? Number(item.subtotal)
                      : Number((item.unit_price || item.price || 0) * item.quantity);
                    return (
                      <div key={idx} className="order-item-row">
                        <div>
                          <span className="order-item-qty">{item.quantity}x</span>
                          <span className="order-item-name">{item.item_name}</span>
                        </div>
                        <span className="order-item-price">
                          ₹{linePrice.toFixed(2)}
                        </span>
                      </div>
                    );
                  })}
                </div>

                <div className="order-footer">
                  <div className="order-total-block">
                    <span className="order-total-label">Total Amount</span>
                    <span className="order-total-val">
                      ₹{Number(order.total_amount).toFixed(2)}
                    </span>
                  </div>

                  <div className="order-actions">
                    {(normStatus === 'PLACED' || normStatus === 'PENDING') && (
                      <button
                        type="button"
                        className="btn btn-primary btn-sm"
                        onClick={() => handleUpdateStatus(order.id, 'PREPARING')}
                        disabled={isUpdating}
                        title="Move order to kitchen preparing"
                      >
                        <ChefHat size={14} />
                        <span>Prepare</span>
                      </button>
                    )}

                    {normStatus === 'PREPARING' && (
                      <button
                        type="button"
                        className="btn btn-success btn-sm"
                        onClick={() => handleUpdateStatus(order.id, 'READY')}
                        disabled={isUpdating}
                        title="Mark order ready for student pickup"
                      >
                        <CheckCircle2 size={14} />
                        <span>Mark Ready</span>
                      </button>
                    )}

                    {normStatus === 'READY' && (
                      <button
                        type="button"
                        className="btn btn-primary btn-sm"
                        onClick={() => handleUpdateStatus(order.id, 'COLLECTED')}
                        disabled={isUpdating}
                        title="Mark as collected by student"
                      >
                        <CheckCircle2 size={14} />
                        <span>Collect</span>
                      </button>
                    )}

                    {normStatus !== 'COLLECTED' && normStatus !== 'COMPLETED' && normStatus !== 'CANCELLED' && (
                      <button
                        type="button"
                        className="btn btn-danger-outline btn-sm"
                        onClick={() => handleUpdateStatus(order.id, 'CANCELLED')}
                        disabled={isUpdating}
                        title="Cancel order"
                      >
                        <XCircle size={14} />
                        <span>Cancel</span>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
