import React, { useState, useEffect } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import {
  X,
  Smartphone,
  QrCode,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
  ArrowRight,
  Ticket,
  ExternalLink,
  RotateCcw,
} from 'lucide-react';

const API_URL = 'http://127.0.0.1:8000';

const UPI_APPS = [
  {
    id: 'gpay',
    name: 'Google Pay',
    shortName: 'GPay',
    color: '#1a73e8',
    bgColor: 'rgba(26, 115, 232, 0.12)',
    borderColor: '#1a73e8',
    handles: ['@okhdfcbank', '@oksbi', '@okaxis', '@okicici'],
    defaultHandle: '@okhdfcbank',
    description: 'Pay via Google Pay UPI',
    badge: 'Fastest',
    badgeColor: '#1a73e8',
  },
  {
    id: 'phonepe',
    name: 'PhonePe',
    shortName: 'PhonePe',
    color: '#5f259f',
    bgColor: 'rgba(95, 37, 159, 0.14)',
    borderColor: '#7c3aed',
    handles: ['@ybl', '@ibl', '@axl'],
    defaultHandle: '@ybl',
    description: 'Pay via PhonePe UPI',
    badge: 'Popular',
    badgeColor: '#8b5cf6',
  },
  {
    id: 'paytm',
    name: 'Paytm UPI',
    shortName: 'Paytm',
    color: '#00b9f5',
    bgColor: 'rgba(0, 185, 245, 0.12)',
    borderColor: '#00b9f5',
    handles: ['@paytm'],
    defaultHandle: '@paytm',
    description: 'Pay using Paytm Wallet / UPI',
  },
  {
    id: 'bhim',
    name: 'BHIM UPI',
    shortName: 'BHIM',
    color: '#00796b',
    bgColor: 'rgba(0, 121, 107, 0.12)',
    borderColor: '#00796b',
    handles: ['@upi'],
    defaultHandle: '@upi',
    description: 'Govt. NPCI Unified Payments Interface',
  },
];

// Authentic, scannable UPI QR Code generated mathematically
function UPIQRCode({ amount, orderId }) {
  const upiId = 'canteen@upi';
  const merchant = 'Smart Canteen';
  const upiLink = `upi://pay?pa=${encodeURIComponent(upiId)}&pn=${encodeURIComponent(merchant)}&am=${amount}&tr=ORD-${orderId}&cu=INR`;

  return (
    <div className="upi-qr-wrapper">
      <div className="upi-qr-box">
        {/* Real mathematical QR Code scannable by any phone camera / GPay / PhonePe */}
        <QRCodeSVG
          value={upiLink}
          size={195}
          level="H"
          includeMargin={true}
          bgColor="#ffffff"
          fgColor="#0f172a"
        />

        <div className="upi-qr-meta">
          <span className="upi-scan-pill">Scan to Pay with Any UPI App</span>
          <div className="upi-app-badges">
            <span style={{ color: '#1a73e8', fontWeight: 700 }}>GPay</span>
            <span>•</span>
            <span style={{ color: '#7c3aed', fontWeight: 700 }}>PhonePe</span>
            <span>•</span>
            <span style={{ color: '#00b9f5', fontWeight: 700 }}>Paytm</span>
            <span>•</span>
            <span style={{ color: '#00796b', fontWeight: 700 }}>BHIM</span>
          </div>
        </div>
      </div>

      <div style={{ marginTop: '0.75rem', textAlign: 'center' }}>
        <a
          href={upiLink}
          className="btn btn-secondary btn-sm"
          style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', textDecoration: 'none' }}
        >
          <ExternalLink size={14} />
          <span>Open UPI App on Mobile</span>
        </a>
      </div>
    </div>
  );
}

export function UPIPaymentModal({ isOpen, onClose, order, onPaymentSuccess }) {
  const [activeTab, setActiveTab] = useState('apps'); // 'apps', 'qr', 'vpa'
  const [selectedApp, setSelectedApp] = useState(UPI_APPS[0]);
  const [phoneOrId, setPhoneOrId] = useState('');
  const [selectedHandle, setSelectedHandle] = useState(UPI_APPS[0].defaultHandle);
  const [customVpa, setCustomVpa] = useState('');

  // Payment execution state: 'idle' | 'processing' | 'success' | 'failed'
  const [paymentState, setPaymentState] = useState('idle');
  const [processingStep, setProcessingStep] = useState(1);
  const [paymentResult, setPaymentResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [copiedUpi, setCopiedUpi] = useState(false);

  // Update default handle when selecting a different app
  const handleSelectApp = (app) => {
    setSelectedApp(app);
    setSelectedHandle(app.defaultHandle);
    setErrorMessage('');
  };

  // Reset state when opening/closing
  useEffect(() => {
    if (isOpen) {
      setPaymentState('idle');
      setProcessingStep(1);
      setPaymentResult(null);
      setErrorMessage('');
      setPhoneOrId('');
      setCustomVpa('');
    }
  }, [isOpen]);

  if (!isOpen || !order) return null;

  const totalAmount = Number(order.total_amount).toFixed(2);

  // Computed UPI ID based on active tab
  const getComputedUpiId = () => {
    if (activeTab === 'apps') {
      const cleanInput = phoneOrId.trim();
      if (!cleanInput) return '';
      // If user already typed @handle, use it, otherwise append selectedHandle
      if (cleanInput.includes('@')) return cleanInput;
      return `${cleanInput}${selectedHandle}`;
    }
    if (activeTab === 'qr') {
      return 'canteen.qr@upi';
    }
    if (activeTab === 'vpa') {
      return customVpa.trim();
    }
    return '';
  };

  const executePayment = async (upiIdToUse, appName = null) => {
    setErrorMessage('');
    const finalUpiId = (upiIdToUse || '').trim().toLowerCase();

    if (!finalUpiId) {
      setErrorMessage('Please enter your mobile number or UPI ID');
      return;
    }

    if (!/^[a-z0-9._-]+@[a-z0-9._-]+$/.test(finalUpiId)) {
      setErrorMessage('Please enter a valid UPI ID (e.g. mobile@okaxis or user@ybl)');
      return;
    }

    setPaymentState('processing');
    setProcessingStep(1);

    try {
      // Step 1: Connecting to UPI provider
      await new Promise((r) => setTimeout(r, 600));
      setProcessingStep(2);

      // Step 2: Awaiting authorization / calling backend
      const token = localStorage.getItem('canteen_student_token');
      const response = await fetch(`${API_URL}/api/orders/${order.id}/payment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          payment_method: 'UPI',
          upi_id: finalUpiId,
          upi_app: appName || selectedApp.name,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Payment could not be processed');
      }

      await new Promise((r) => setTimeout(r, 600));
      setProcessingStep(3);

      if (data.status === 'SUCCESS') {
        setPaymentResult(data);
        setPaymentState('success');
        if (onPaymentSuccess) {
          onPaymentSuccess(data, data.token_code);
        }
      } else {
        setPaymentState('failed');
        setErrorMessage('UPI Payment was declined by your bank simulator. Please try again.');
      }
    } catch (err) {
      setPaymentState('failed');
      setErrorMessage(err.message || 'Payment transaction failed. Please retry.');
    }
  };

  const copyUpiId = () => {
    navigator.clipboard?.writeText('canteen@upi');
    setCopiedUpi(true);
    setTimeout(() => setCopiedUpi(false), 2000);
  };

  return (
    <div className="modal-backdrop" onClick={paymentState !== 'processing' ? onClose : undefined}>
      <div className="modal-card upi-modal-card" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className="upi-logo-chip">UPI</span>
              <h3 style={{ margin: 0, fontSize: '1.2rem' }}>Pay via UPI</h3>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginTop: 2 }}>
              Order #{order.id} • Amount: <strong style={{ color: 'var(--color-primary)' }}>₹{totalAmount}</strong>
            </div>
          </div>
          {paymentState !== 'processing' && (
            <button
              type="button"
              className="btn btn-secondary btn-icon"
              onClick={onClose}
              aria-label="Close"
            >
              <X size={18} />
            </button>
          )}
        </div>

        {/* Modal Body */}
        <div className="modal-body">
          {/* PROCESSING STATE */}
          {paymentState === 'processing' && (
            <div className="upi-state-container">
              <div className="upi-pulse-spinner">
                <span className="spinner" style={{ width: 44, height: 44, borderWidth: 3 }}></span>
              </div>
              <h4 style={{ margin: '1rem 0 0.25rem 0' }}>Authorizing UPI Payment</h4>
              <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem', maxWidth: 360, textAlign: 'center' }}>
                {processingStep === 1 && 'Connecting to Unified Payments Interface gateway...'}
                {processingStep === 2 && `Sending approval request to ${selectedApp.name} (${getComputedUpiId()})...`}
                {processingStep === 3 && 'Payment verified! Generating digital food token...'}
              </p>

              <div className="upi-steps-indicator">
                <div className={`upi-step ${processingStep >= 1 ? 'completed' : ''}`}>
                  <div className="upi-step-dot">1</div>
                  <span>Initialize</span>
                </div>
                <div className={`upi-step-line ${processingStep >= 2 ? 'active' : ''}`}></div>
                <div className={`upi-step ${processingStep >= 2 ? 'completed' : ''}`}>
                  <div className="upi-step-dot">2</div>
                  <span>Approve</span>
                </div>
                <div className={`upi-step-line ${processingStep >= 3 ? 'active' : ''}`}></div>
                <div className={`upi-step ${processingStep >= 3 ? 'completed' : ''}`}>
                  <div className="upi-step-dot">3</div>
                  <span>Issue Token</span>
                </div>
              </div>

              <div style={{ fontSize: '0.78rem', color: 'var(--color-text-dim)', marginTop: '1.25rem' }}>
                Please do not refresh or close this window
              </div>
            </div>
          )}

          {/* SUCCESS STATE */}
          {paymentState === 'success' && paymentResult && (
            <div className="upi-state-container">
              <div className="upi-success-icon-wrap">
                <CheckCircle2 size={46} color="#10b981" />
              </div>
              <h3 style={{ margin: '0.75rem 0 0.25rem 0', color: '#10b981' }}>Payment Successful!</h3>
              <p style={{ color: 'var(--color-text-muted)', fontSize: '0.88rem', margin: 0 }}>
                ₹{totalAmount} paid via UPI ({paymentResult.payment_method})
              </p>

              {paymentResult.token_code && (
                <div className="upi-token-box">
                  <div className="upi-token-label">
                    <Ticket size={16} />
                    <span>YOUR CANTEEN PICKUP TOKEN</span>
                  </div>
                  <div className="upi-token-code">{paymentResult.token_code}</div>
                  <div className="upi-token-hint">
                    Show this token at the canteen pickup counter when your order is ready!
                  </div>
                </div>
              )}

              {paymentResult.transaction_reference && (
                <div className="upi-txn-ref">
                  <span>Transaction Ref:</span>
                  <code>{paymentResult.transaction_reference}</code>
                </div>
              )}

              <button
                type="button"
                className="btn btn-primary"
                onClick={onClose}
                style={{ marginTop: '1rem', width: '100%', maxWidth: 280 }}
              >
                Done
              </button>
            </div>
          )}

          {/* FAILED STATE */}
          {paymentState === 'failed' && (
            <div className="upi-state-container">
              <div className="upi-failed-icon-wrap">
                <AlertCircle size={46} color="#ef4444" />
              </div>
              <h3 style={{ margin: '0.75rem 0 0.25rem 0', color: '#ef4444' }}>Payment Failed</h3>
              <p style={{ color: 'var(--color-text-muted)', fontSize: '0.88rem', maxWidth: 360, textAlign: 'center' }}>
                {errorMessage || 'Your UPI transaction could not be completed.'}
              </p>

              <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1.25rem' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setPaymentState('idle')}
                >
                  <RotateCcw size={15} />
                  <span>Try Again</span>
                </button>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={onClose}
                >
                  Close
                </button>
              </div>
            </div>
          )}

          {/* MAIN PAYMENT FORM (IDLE) */}
          {paymentState === 'idle' && (
            <>
              {/* Payment Mode Selector Tabs */}
              <div className="upi-tab-nav">
                <button
                  type="button"
                  className={`upi-tab-btn ${activeTab === 'apps' ? 'active' : ''}`}
                  onClick={() => { setActiveTab('apps'); setErrorMessage(''); }}
                >
                  <Smartphone size={16} />
                  <span>UPI Apps</span>
                </button>
                <button
                  type="button"
                  className={`upi-tab-btn ${activeTab === 'qr' ? 'active' : ''}`}
                  onClick={() => { setActiveTab('qr'); setErrorMessage(''); }}
                >
                  <QrCode size={16} />
                  <span>Scan QR</span>
                </button>
                <button
                  type="button"
                  className={`upi-tab-btn ${activeTab === 'vpa' ? 'active' : ''}`}
                  onClick={() => { setActiveTab('vpa'); setErrorMessage(''); }}
                >
                  <span>Any UPI ID</span>
                </button>
              </div>

              {errorMessage && (
                <div className="toast toast-error" style={{ position: 'static', margin: '0.5rem 0' }}>
                  {errorMessage}
                </div>
              )}

              {/* TAB 1: POPULAR UPI APPS (Google Pay, PhonePe, Paytm, BHIM) */}
              {activeTab === 'apps' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <label className="form-label" style={{ marginBottom: 0 }}>Select your UPI app</label>
                  <div className="upi-apps-grid">
                    {UPI_APPS.map((app) => {
                      const isSelected = selectedApp.id === app.id;
                      return (
                        <div
                          key={app.id}
                          className={`upi-app-card ${isSelected ? 'active' : ''}`}
                          onClick={() => handleSelectApp(app)}
                          style={{ borderColor: isSelected ? app.borderColor : undefined }}
                        >
                          <div
                            className="upi-app-icon-circle"
                            style={{ backgroundColor: app.bgColor, color: app.color }}
                          >
                            <span style={{ fontWeight: 800, fontSize: '0.85rem' }}>
                              {app.shortName.slice(0, 2).toUpperCase()}
                            </span>
                          </div>
                          <div className="upi-app-info">
                            <div className="upi-app-name-row">
                              <span className="upi-app-title">{app.name}</span>
                              {app.badge && (
                                <span
                                  className="upi-mini-badge"
                                  style={{ color: app.badgeColor, background: app.bgColor }}
                                >
                                  {app.badge}
                                </span>
                              )}
                            </div>
                            <span className="upi-app-sub">{app.defaultHandle}</span>
                          </div>
                          <div className={`upi-radio-circle ${isSelected ? 'checked' : ''}`}></div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Phone / User ID input for selected app */}
                  <div className="form-group" style={{ marginTop: '0.25rem' }}>
                    <label className="form-label">
                      Enter Mobile Number or ID for {selectedApp.name}
                    </label>
                    <div className="upi-input-group">
                      <input
                        type="text"
                        className="form-control"
                        placeholder="e.g. 9876543210 or yourname"
                        value={phoneOrId}
                        onChange={(e) => setPhoneOrId(e.target.value)}
                        autoFocus
                      />
                      <span className="upi-input-addon">{selectedHandle}</span>
                    </div>

                    {/* Suffix handle pills if app has multiple */}
                    {selectedApp.handles.length > 1 && (
                      <div className="upi-handle-pills">
                        <span style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)' }}>Bank:</span>
                        {selectedApp.handles.map((h) => (
                          <button
                            key={h}
                            type="button"
                            className={`upi-pill ${selectedHandle === h ? 'active' : ''}`}
                            onClick={() => setSelectedHandle(h)}
                          >
                            {h}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Pay button */}
                  <button
                    type="button"
                    className="btn btn-primary"
                    style={{ width: '100%', padding: '0.75rem', fontSize: '1rem', marginTop: '0.25rem' }}
                    onClick={() => executePayment(getComputedUpiId(), selectedApp.name)}
                  >
                    <span>Pay ₹{totalAmount} with {selectedApp.name}</span>
                    <ArrowRight size={18} />
                  </button>
                </div>
              )}

              {/* TAB 2: SCAN UPI QR CODE */}
              {activeTab === 'qr' && (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.75rem' }}>
                  <UPIQRCode amount={totalAmount} orderId={order.id} />

                  <div className="upi-merchant-box">
                    <div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)' }}>UPI ID</div>
                      <code style={{ fontSize: '0.9rem', color: 'var(--color-text)' }}>canteen@upi</code>
                    </div>
                    <button
                      type="button"
                      className="btn btn-secondary btn-sm"
                      onClick={copyUpiId}
                      style={{ padding: '0.3rem 0.6rem' }}
                    >
                      {copiedUpi ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
                      <span>{copiedUpi ? 'Copied' : 'Copy'}</span>
                    </button>
                  </div>

                  <button
                    type="button"
                    className="btn btn-primary"
                    style={{ width: '100%', padding: '0.75rem', marginTop: '0.5rem' }}
                    onClick={() => executePayment('canteen.qr@upi', 'UPI QR')}
                  >
                    <span>I Have Paid · Verify ₹{totalAmount}</span>
                    <Check size={18} />
                  </button>
                </div>
              )}

              {/* TAB 3: ANY CUSTOM UPI ID */}
              {activeTab === 'vpa' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <div className="form-group">
                    <label className="form-label">Enter Virtual Payment Address (VPA)</label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="e.g. yourname@okhdfcbank or 9876543210@ybl"
                      value={customVpa}
                      onChange={(e) => setCustomVpa(e.target.value)}
                      autoFocus
                    />
                  </div>

                  {/* Quick handle suggestions */}
                  <div>
                    <label className="form-label" style={{ fontSize: '0.78rem' }}>Quick append handle:</label>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                      {['@okhdfcbank', '@oksbi', '@ybl', '@paytm', '@upi'].map((h) => (
                        <button
                          key={h}
                          type="button"
                          className="upi-pill"
                          onClick={() => {
                            const base = customVpa.split('@')[0] || '';
                            setCustomVpa(base ? `${base}${h}` : `student${h}`);
                          }}
                        >
                          {h}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="demo-credentials-box" style={{ fontSize: '0.8rem', marginTop: '0.25rem' }}>
                    <div>💡 <strong>Testing failure simulation:</strong> Enter <code>fail@upi</code> to test bank decline handling.</div>
                  </div>

                  <button
                    type="button"
                    className="btn btn-primary"
                    style={{ width: '100%', padding: '0.75rem', fontSize: '1rem', marginTop: '0.25rem' }}
                    onClick={() => executePayment(customVpa, 'Custom UPI')}
                  >
                    <span>Verify & Pay ₹{totalAmount}</span>
                    <ArrowRight size={18} />
                  </button>
                </div>
              )}

              {/* Footer Trust Shield */}
              <div className="upi-trust-footer">
                <ShieldCheck size={16} color="#10b981" />
                <span>NPCI UPI 256-bit Encrypted • Instant Food Token Generation</span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
