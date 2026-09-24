import React, { createContext, useContext, useState, useEffect } from 'react';
import { AdminAPI } from '../api/admin';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function verifyAuth() {
      const token = localStorage.getItem('canteen_staff_token');
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const profile = await AdminAPI.getMe();
        const role = (profile?.role || '').toUpperCase();
        if (role === 'STAFF' || role === 'ADMIN') {
          setUser({
            id: profile.id,
            username: profile.email || profile.name,
            email: profile.email,
            role,
            fullName: profile.name,
          });
        } else {
          // Non-staff user cannot use the admin panel
          localStorage.removeItem('canteen_staff_token');
          setUser(null);
        }
      } catch (err) {
        localStorage.removeItem('canteen_staff_token');
        setUser(null);
      } finally {
        setLoading(false);
      }
    }

    verifyAuth();
  }, []);

  const login = async (username, password) => {
    const data = await AdminAPI.login(username, password);
    const role = (data.user?.role || data.role || '').toUpperCase();
    if (role !== 'STAFF' && role !== 'ADMIN') {
      throw new Error('Access denied: account does not have canteen staff privileges');
    }
    localStorage.setItem('canteen_staff_token', data.access_token);
    const userObj = {
      id: data.user?.id || data.id,
      username: data.user?.email || data.username || username,
      email: data.user?.email || data.email,
      role,
      fullName: data.user?.name || data.full_name || 'Canteen Staff',
    };
    setUser(userObj);
    return data;
  };

  const logout = () => {
    localStorage.removeItem('canteen_staff_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
