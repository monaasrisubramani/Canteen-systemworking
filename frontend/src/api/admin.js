import { apiRequest } from './client';

export const AdminAPI = {
  // Authentication
  async login(username, password) {
    return apiRequest('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email: username, password }),
    });
  },

  async getMe() {
    return apiRequest('/api/auth/me');
  },

  // Operational Summary
  async getSummary() {
    return apiRequest('/api/admin/summary');
  },

  // Orders Management
  async getOrders(status = null) {
    const query = status && status !== 'All' ? `?status=${encodeURIComponent(status)}` : '';
    return apiRequest(`/api/admin/orders${query}`);
  },

  async updateOrderStatus(orderId, status) {
    return apiRequest(`/api/admin/orders/${orderId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  },

  // Menu Management
  async getMenuItems(category = null, availableOnly = false) {
    const params = new URLSearchParams();
    if (category && category !== 'All') {
      params.append('category', category);
    }
    if (availableOnly) {
      params.append('available_only', 'true');
    }
    const query = params.toString() ? `?${params.toString()}` : '';
    return apiRequest(`/api/admin/menu${query}`);
  },

  async createMenuItem(data) {
    return apiRequest('/api/admin/menu', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updateMenuItem(id, data) {
    return apiRequest(`/api/admin/menu/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async deleteMenuItem(id) {
    return apiRequest(`/api/admin/menu/${id}`, {
      method: 'DELETE',
    });
  },

  async toggleAvailability(id, isAvailable = null) {
    const body = isAvailable !== null ? JSON.stringify({ is_available: isAvailable }) : undefined;
    return apiRequest(`/api/admin/menu/${id}/availability`, {
      method: 'PATCH',
      body,
    });
  },
};
