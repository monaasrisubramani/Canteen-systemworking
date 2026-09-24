import React from 'react';
import {
  LayoutDashboard,
  ClipboardList,
  UtensilsCrossed,
  ToggleLeft,
  LogOut,
  ChefHat,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export function Navbar({ activeTab, setActiveTab }) {
  const { user, logout } = useAuth();

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'orders', label: 'Incoming Orders', icon: ClipboardList },
    { id: 'menu', label: 'Menu Items', icon: UtensilsCrossed },
    { id: 'availability', label: 'Availability', icon: ToggleLeft },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <div className="brand" onClick={() => setActiveTab('dashboard')}>
          <div className="brand-icon">
            <ChefHat size={22} />
          </div>
          <div className="brand-text">
            <h1>Smart Canteen</h1>
            <span>Staff Administration</span>
          </div>
        </div>

        <div className="nav-links">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                type="button"
                className={`nav-item ${isActive ? 'active' : ''}`}
                onClick={() => setActiveTab(item.id)}
              >
                <Icon size={16} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>

        <div className="nav-user">
          <div className="user-badge">
            <div className="user-avatar">
              {(user?.fullName || user?.username || 'S')[0].toUpperCase()}
            </div>
            <div className="user-info">
              <div className="user-name">{user?.fullName || user?.username}</div>
              <div className="user-role">{user?.role}</div>
            </div>
          </div>

          <button
            type="button"
            className="btn-logout"
            onClick={logout}
            title="Log out of staff panel"
          >
            <LogOut size={16} />
            <span>Logout</span>
          </button>
        </div>
      </div>
    </nav>
  );
}
