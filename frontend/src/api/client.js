const API_BASE_URL = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
  ? 'http://127.0.0.1:8000'
  : '';

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('canteen_staff_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });
  } catch (err) {
    throw new Error('Cannot connect to backend server. Please ensure the FastAPI backend is running on http://127.0.0.1:8000.');
  }

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    let message = 'An unexpected error occurred';
    if (typeof data.detail === 'string') {
      message = data.detail;
    } else if (Array.isArray(data.detail) && data.detail.length > 0) {
      message = data.detail.map((d) => d.msg || JSON.stringify(d)).join('; ');
    } else if (data.message && typeof data.message === 'string') {
      message = data.message;
    } else if (typeof data === 'string' && data.length > 0) {
      message = data;
    } else if (response.statusText) {
      message = `${response.status} ${response.statusText}`;
    }
    const error = new Error(message);
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}
