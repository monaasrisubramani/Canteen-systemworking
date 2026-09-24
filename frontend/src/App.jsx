import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { ToastContainer } from './components/Toast';
import { AdminLogin } from './pages/admin/AdminLogin';
import { AdminDashboard } from './pages/admin/AdminDashboard';
import { OrderManagement } from './pages/admin/OrderManagement';
import { MenuManagement } from './pages/admin/MenuManagement';
import { StudentPortal } from './pages/student/StudentPortal';

const API_URL = 'http://127.0.0.1:8000';

function RoleLogin({ onStudentLogin }) {
  const [isRegistering, setIsRegistering] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setLoading(true); setError('');
    try {
      const path = isRegistering ? '/api/auth/register' : '/api/auth/login';
      const payload = isRegistering ? { name, email, password } : { email, password };
      const response = await fetch(`${API_URL}${path}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Login failed');
      if ((data.user?.role || '').toUpperCase() === 'ADMIN') {
        localStorage.setItem('canteen_staff_token', data.access_token);
        window.location.reload();
        return;
      }
      if ((data.user?.role || '').toUpperCase() === 'STUDENT') {
        localStorage.setItem('canteen_student_token', data.access_token);
        onStudentLogin(data.user);
        return;
      }
      throw new Error('This account does not have access to a portal.');
    } catch (loginError) { setError(loginError.message); } finally { setLoading(false); }
  };

  return <div className="login-container"><div className="login-card"><div className="login-header"><div className="brand-icon" style={{ width: 52, height: 52 }}>🍽️</div><h2>Smart Canteen</h2><p>{isRegistering ? 'Create your student account to order food.' : 'Sign in as a student or canteen administrator.'}</p></div>{error && <div className="toast toast-error" style={{ position: 'static' }}>{error}</div>}<form onSubmit={submit} style={{ display: 'grid', gap: '1rem' }}>{isRegistering && <div className="form-group"><label className="form-label">Full name</label><input className="form-control" value={name} onChange={(event) => setName(event.target.value)} placeholder="Your full name" minLength="2" required /></div>}<div className="form-group"><label className="form-label">Email</label><input className="form-control" type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="student@example.com" required /></div><div className="form-group"><label className="form-label">Password</label><input className="form-control" type="password" value={password} onChange={(event) => setPassword(event.target.value)} minLength="6" required /></div><button className="btn btn-primary" disabled={loading}>{loading ? 'Please wait…' : isRegistering ? 'Create student account' : 'Sign in'}</button></form><button className="btn btn-secondary" type="button" onClick={() => { setIsRegistering(!isRegistering); setError(''); }}>{isRegistering ? 'Already registered? Sign in' : 'New student? Create an account'}</button>{!isRegistering && <div className="demo-credentials-box"><div>Existing student: <code>student@example.com</code> / <code>prototype-password</code></div><div style={{ marginTop: '.4rem' }}>Admin: <code>admin@example.com</code> / <code>prototype-password</code></div></div>}</div></div>;
}

function AdminApp() {
  const { user, loading } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [toasts, setToasts] = useState([]);
  const [triggerAddMenu, setTriggerAddMenu] = useState(false);

  const showToast = (message, type = 'info') => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  const dismissToast = (id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  if (loading) {
    return (
      <div className="state-box" style={{ minHeight: '100vh' }}>
        <div className="spinner"></div>
        <p>Verifying staff authorization...</p>
      </div>
    );
  }

  if (!user) {
    return <AdminLogin />;
  }

  return (
    <div className="app-container">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="main-content">
        {activeTab === 'dashboard' && (
          <AdminDashboard
            setActiveTab={setActiveTab}
            onAddMenuItemClick={() => {
              setActiveTab('menu');
              setTriggerAddMenu(true);
            }}
          />
        )}

        {activeTab === 'orders' && <OrderManagement onShowToast={showToast} />}

        {activeTab === 'menu' && (
          <MenuManagement
            onShowToast={showToast}
            isAvailabilityOnlyView={false}
            triggerAddModal={triggerAddMenu}
            onResetTriggerAddModal={() => setTriggerAddMenu(false)}
          />
        )}

        {activeTab === 'availability' && (
          <MenuManagement onShowToast={showToast} isAvailabilityOnlyView={true} />
        )}
      </main>

      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
}

export default function App() {
  const [student, setStudent] = useState(() => JSON.parse(localStorage.getItem('canteen_student_user') || 'null'));
  const finishStudentLogin = (user) => { localStorage.setItem('canteen_student_user', JSON.stringify(user)); setStudent(user); };
  const studentLogout = () => { localStorage.removeItem('canteen_student_token'); localStorage.removeItem('canteen_student_user'); setStudent(null); };

  if (student) return <StudentPortal user={student} onLogout={studentLogout} />;
  if (!localStorage.getItem('canteen_staff_token')) return <RoleLogin onStudentLogin={finishStudentLogin} />;
  return (
    <AuthProvider>
      <AdminApp />
    </AuthProvider>
  );
}
