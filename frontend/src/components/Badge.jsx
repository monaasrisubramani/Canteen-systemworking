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
