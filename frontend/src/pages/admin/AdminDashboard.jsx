import React, { useEffect, useState } from 'react';
import {
  Clock,
  ChefHat,
  CheckCircle2,
  UtensilsCrossed,
  ToggleRight,
  ClipboardList,
  RefreshCw,
  PlusCircle,
  AlertCircle,
  ArrowRight,
} from 'lucide-react';
import { AdminAPI } from '../../api/admin';
import { StatusBadge } from '../../components/Badge';

export function AdminDashboard({ setActiveTab, onAddMenuItemClick }) {
  const [summary, setSummary] = useState(null);
  const [recentOrders, setRecentOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadDashboardData = async () => {
    setLoading(true);
    setError('');
    try {
      const [sumData, ordersData] = await Promise.all([
        AdminAPI.getSummary(),
        AdminAPI.getOrders(),
      ]);
      setSummary(sumData);
      setRecentOrders((ordersData || []).slice(0, 5));
    } catch (err) {
      setError(err.message || 'Failed to load dashboard metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const metrics = [
    {
      label: 'Incoming / Placed',
      value: summary?.placed_orders ?? summary?.pending_orders ?? 0,
      icon: Clock,
      color: '#f59e0b',
      bg: 'rgba(245, 158, 11, 0.12)',
      onClick: () => setActiveTab('orders'),
    },
    {
      label: 'Preparing Orders',
      value: summary?.preparing_orders ?? 0,
      icon: ChefHat,
      color: '#06b6d4',
      bg: 'rgba(6, 182, 212, 0.12)',
      onClick: () => setActiveTab('orders'),
    },
    {
      label: 'Ready / Collected',
      value: (summary?.ready_orders ?? 0) + (summary?.collected_orders ?? summary?.completed_orders ?? 0),
      icon: CheckCircle2,
      color: '#10b981',
      bg: 'rgba(16, 185, 129, 0.12)',
      onClick: () => setActiveTab('orders'),
    },
    {
      label: 'Available Items',
      value: summary?.available_menu_items ?? 0,
      icon: UtensilsCrossed,
      color: '#10b981',
      bg: 'rgba(16, 185, 129, 0.12)',
      onClick: () => setActiveTab('menu'),
    },
    {
      label: 'Unavailable Items',
      value: summary?.unavailable_menu_items ?? 0,
      icon: ToggleRight,
      color: '#ef4444',
      bg: 'rgba(239, 68, 68, 0.12)',
      onClick: () => setActiveTab('availability'),
    },
  ];

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          <h2>Canteen Operations Overview</h2>
          <p>Real-time volume metrics, active orders, and menu item readiness</p>
        </div>
        <div className="page-actions">
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={loadDashboardData}
            disabled={loading}
          >
            <RefreshCw size={15} className={loading ? 'spinner' : ''} />
            <span>Refresh</span>
          </button>
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={onAddMenuItemClick}
          >
            <PlusCircle size={15} />
            <span>Add Menu Item</span>
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

      {/* Summary Cards */}
      <div className="metrics-grid">
        {metrics.map((m, idx) => {
          const Icon = m.icon;
          return (
            <div
              key={idx}
              className="metric-card"
              onClick={m.onClick}
              style={{ cursor: 'pointer' }}
              title={`Click to view ${m.label}`}
            >
              <div className="metric-icon" style={{ backgroundColor: m.bg, color: m.color }}>
                <Icon size={24} />
              </div>
              <div className="metric-data">
                <div className="metric-value">
                  {loading ? '-' : m.value}
                </div>
                <div className="metric-label">{m.label}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Navigation Quick Actions */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem', marginBottom: '2rem' }}>
        <div
          className="card-container"
          style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.75rem', cursor: 'pointer' }}
          onClick={() => setActiveTab('orders')}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div className="metric-icon" style={{ backgroundColor: 'rgba(234, 88, 12, 0.15)', color: 'var(--color-primary)' }}>
                <ClipboardList size={22} />
              </div>
              <div>
                <h4 style={{ fontSize: '1.05rem', color: 'var(--color-text)' }}>Incoming Orders</h4>
                <p style={{ fontSize: '0.82rem', color: 'var(--color-text-muted)' }}>Manage live incoming orders & status transitions</p>
              </div>
            </div>
            <ArrowRight size={18} color="var(--color-text-dim)" />
          </div>
        </div>

        <div
          className="card-container"
          style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.75rem', cursor: 'pointer' }}
          onClick={() => setActiveTab('menu')}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div className="metric-icon" style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', color: 'var(--color-success)' }}>
                <UtensilsCrossed size={22} />
              </div>
              <div>
                <h4 style={{ fontSize: '1.05rem', color: 'var(--color-text)' }}>Menu Management</h4>
                <p style={{ fontSize: '0.82rem', color: 'var(--color-text-muted)' }}>Add, edit, remove food items, prices and categories</p>
              </div>
            </div>
            <ArrowRight size={18} color="var(--color-text-dim)" />
          </div>
        </div>

        <div
          className="card-container"
          style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.75rem', cursor: 'pointer' }}
          onClick={() => setActiveTab('availability')}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div className="metric-icon" style={{ backgroundColor: 'rgba(6, 182, 212, 0.15)', color: 'var(--color-info)' }}>
                <ToggleRight size={22} />
              </div>
              <div>
                <h4 style={{ fontSize: '1.05rem', color: 'var(--color-text)' }}>Food Availability</h4>
                <p style={{ fontSize: '0.82rem', color: 'var(--color-text-muted)' }}>Quick kitchen toggle for items in and out of stock</p>
              </div>
            </div>
            <ArrowRight size={18} color="var(--color-text-dim)" />
          </div>
        </div>
      </div>

      {/* Recent Orders Glance */}
      <div className="card-container">
        <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--color-border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h3 style={{ fontSize: '1.1rem', color: 'var(--color-text)' }}>Recent Incoming Orders</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--color-text-dim)' }}>Latest student orders placed at the counter or online</p>
          </div>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => setActiveTab('orders')}
          >
            <span>View All Orders</span>
            <ArrowRight size={14} />
          </button>
        </div>

        {loading ? (
          <div className="state-box">
            <div className="spinner"></div>
            <p>Loading recent orders...</p>
          </div>
        ) : recentOrders.length === 0 ? (
          <div className="state-box">
            <ClipboardList />
            <h4>No incoming orders yet</h4>
            <p>Orders placed by students will appear here in real-time.</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Order ID</th>
                  <th>Customer</th>
                  <th>Items</th>
                  <th>Total</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {recentOrders.map((order) => (
                  <tr key={order.id}>
                    <td>
                      <span style={{ fontWeight: 700, color: 'var(--color-text)' }}>#{order.id}</span>
                    </td>
                    <td>
                      <div style={{ fontWeight: 600 }}>{order.customer_name}</div>
                      {order.student_id && (
                        <div style={{ fontSize: '0.78rem', color: 'var(--color-text-dim)' }}>
                          {order.student_id}
                        </div>
                      )}
                    </td>
                    <td>
                      <div style={{ fontSize: '0.85rem' }}>
                        {(order.items || []).map((i) => `${i.quantity}x ${i.item_name}`).join(', ')}
                      </div>
                    </td>
                    <td>
                      <span style={{ fontWeight: 700, color: 'var(--color-primary)' }}>
                        ₹{Number(order.total_amount).toFixed(2)}
                      </span>
                    </td>
                    <td>
                      <StatusBadge status={order.status} />
                    </td>
                    <td>
                      <button
                        type="button"
                        className="btn btn-secondary btn-sm"
                        onClick={() => setActiveTab('orders')}
                      >
                        Manage
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
