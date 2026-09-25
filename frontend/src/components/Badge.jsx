import React from 'react';

export function StatusBadge({ status }) {
  const normalized = (status || '').toLowerCase();
  let badgeClass = 'badge-pending';

  switch (normalized) {
    case 'placed':
    case 'pending':
      badgeClass = 'badge-pending';
      break;
    case 'preparing':
      badgeClass = 'badge-preparing';
      break;
    case 'ready':
      badgeClass = 'badge-ready';
      break;
    case 'collected':
    case 'completed':
      badgeClass = 'badge-completed';
      break;
    case 'cancelled':
      badgeClass = 'badge-cancelled';
      break;
    default:
      badgeClass = 'badge-pending';
  }

  return (
    <span className={`badge ${badgeClass}`}>
      <span style={{
        width: 6,
        height: 6,
        borderRadius: '50%',
        backgroundColor: 'currentColor',
        display: 'inline-block'
      }}></span>
      {status}
    </span>
  );
}

export function AvailabilityBadge({ isAvailable }) {
  return (
    <span className={`badge ${isAvailable ? 'badge-available' : 'badge-unavailable'}`}>
      <span style={{
        width: 6,
        height: 6,
        borderRadius: '50%',
        backgroundColor: 'currentColor',
        display: 'inline-block'
      }}></span>
      {isAvailable ? 'Available' : 'Unavailable'}
    </span>
  );
}

export function PaymentBadge({ status }) {
  const norm = (status || '').toUpperCase();
  if (norm === 'SUCCESS' || norm === 'PAID') {
    return (
      <span
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.35rem',
          padding: '0.2rem 0.6rem',
          borderRadius: 'var(--radius-full)',
          background: 'rgba(16, 185, 129, 0.15)',
          color: '#10b981',
          border: '1px solid rgba(16, 185, 129, 0.35)',
          fontSize: '0.75rem',
          fontWeight: 600,
        }}
      >
        <span style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: '#10b981', display: 'inline-block' }}></span>
        Paid via UPI
      </span>
    );
  }
  if (norm === 'FAILED') {
    return (
      <span
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.35rem',
          padding: '0.2rem 0.6rem',
          borderRadius: 'var(--radius-full)',
          background: 'rgba(239, 68, 68, 0.15)',
          color: '#ef4444',
          border: '1px solid rgba(239, 68, 68, 0.35)',
          fontSize: '0.75rem',
          fontWeight: 600,
        }}
      >
        <span style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: '#ef4444', display: 'inline-block' }}></span>
        UPI Failed
      </span>
    );
  }
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.35rem',
        padding: '0.2rem 0.6rem',
        borderRadius: 'var(--radius-full)',
        background: 'rgba(245, 158, 11, 0.15)',
        color: '#f59e0b',
        border: '1px solid rgba(245, 158, 11, 0.35)',
        fontSize: '0.75rem',
        fontWeight: 600,
      }}
    >
      <span style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: '#f59e0b', display: 'inline-block' }}></span>
      Payment Pending
    </span>
  );
}
