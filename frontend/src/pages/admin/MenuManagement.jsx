import React, { useEffect, useState, useCallback } from 'react';
import {
  UtensilsCrossed,
  Plus,
  Edit2,
  Trash2,
  Search,
  RefreshCw,
  AlertCircle,
  ToggleLeft,
  ToggleRight,
  Check,
  AlertTriangle,
} from 'lucide-react';
import { AdminAPI } from '../../api/admin';
import { AvailabilityBadge } from '../../components/Badge';
import { Modal } from '../../components/Modal';

export function MenuManagement({ onShowToast, isAvailabilityOnlyView = false, triggerAddModal = false, onResetTriggerAddModal }) {
  const [menuItems, setMenuItems] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [togglingId, setTogglingId] = useState(null);

  // Add/Edit Modal State
  const [modalOpen, setModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    category: 'General',
    image_url: '',
    is_available: true,
  });
  const [formErrors, setFormErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  // Delete Confirmation Modal State
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const categories = ['All', 'Breakfast', 'Lunch', 'Snacks', 'Beverages', 'Desserts', 'General'];

  const fetchMenu = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await AdminAPI.getMenuItems(selectedCategory);
      setMenuItems(data || []);
    } catch (err) {
      setError(err.message || 'Failed to load menu items');
    } finally {
      setLoading(false);
    }
  }, [selectedCategory]);

  useEffect(() => {
    fetchMenu();
  }, [fetchMenu]);

  // Handle trigger to open add modal from dashboard
  useEffect(() => {
    if (triggerAddModal) {
      handleOpenAddModal();
      if (onResetTriggerAddModal) onResetTriggerAddModal();
    }
  }, [triggerAddModal]);

  const handleOpenAddModal = () => {
    setEditingItem(null);
    setFormData({
      name: '',
      description: '',
      price: '',
      category: 'General',
      image_url: '',
      is_available: true,
    });
    setFormErrors({});
    setModalOpen(true);
  };

  const handleOpenEditModal = (item) => {
    setEditingItem(item);
    setFormData({
      name: item.name,
      description: item.description || '',
      price: String(item.price),
      category: item.category || 'General',
      image_url: item.image_url || '',
      is_available: item.is_available,
    });
    setFormErrors({});
    setModalOpen(true);
  };

  const handleOpenDeleteModal = (item) => {
    setItemToDelete(item);
    setDeleteModalOpen(true);
  };

  // Form input validation
  const validateForm = () => {
    const errors = {};
    if (!formData.name.trim()) {
      errors.name = 'Item name is required and cannot be blank';
    } else if (formData.name.trim().length > 100) {
      errors.name = 'Item name must be 100 characters or less';
    }

    if (formData.price === '' || isNaN(Number(formData.price))) {
      errors.price = 'Valid price is required';
    } else if (Number(formData.price) < 0) {
      errors.price = 'Price must be non-negative (0 or greater)';
    }

    if (!formData.category.trim()) {
      errors.category = 'Category is required';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSaveItem = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setSubmitting(true);
    const payload = {
      name: formData.name.trim(),
      description: formData.description.trim() || '',
      price: parseFloat(formData.price),
      category: formData.category.trim(),
      is_available: formData.is_available,
    };

    try {
      if (editingItem) {
        const updated = await AdminAPI.updateMenuItem(editingItem.id, payload);
        setMenuItems((prev) =>
          prev.map((i) => (i.id === editingItem.id ? updated : i))
        );
        if (onShowToast) {
          onShowToast(`Menu item "${updated.name}" updated successfully`, 'success');
        }
      } else {
        const created = await AdminAPI.createMenuItem(payload);
        setMenuItems((prev) => [...prev, created]);
        if (onShowToast) {
          onShowToast(`Menu item "${created.name}" created successfully`, 'success');
        }
      }
      setModalOpen(false);
    } catch (err) {
      if (onShowToast) {
        onShowToast(err.message || 'Operation failed', 'error');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteItem = async () => {
    if (!itemToDelete) return;
    setDeleting(true);
    try {
      await AdminAPI.deleteMenuItem(itemToDelete.id);
      setMenuItems((prev) => prev.filter((i) => i.id !== itemToDelete.id));
      if (onShowToast) {
        onShowToast(`"${itemToDelete.name}" removed from menu`, 'success');
      }
      setDeleteModalOpen(false);
      setItemToDelete(null);
    } catch (err) {
      if (onShowToast) {
        onShowToast(err.message || 'Failed to remove menu item', 'error');
      }
    } finally {
      setDeleting(false);
    }
  };

  const handleToggleAvailability = async (item) => {
    setTogglingId(item.id);
    const nextState = !item.is_available;
    try {
      const updated = await AdminAPI.toggleAvailability(item.id, nextState);
      setMenuItems((prev) =>
        prev.map((i) => (i.id === item.id ? { ...i, is_available: updated.is_available } : i))
      );
      if (onShowToast) {
        onShowToast(
          `"${item.name}" marked as ${updated.is_available ? 'Available' : 'Unavailable'}`,
          'success'
        );
      }
    } catch (err) {
      if (onShowToast) {
        onShowToast(err.message || `Failed to toggle availability for "${item.name}"`, 'error');
      }
    } finally {
      setTogglingId(null);
    }
  };

  const filteredItems = menuItems.filter((item) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    const nameMatch = item.name.toLowerCase().includes(q);
    const catMatch = item.category.toLowerCase().includes(q);
    const descMatch = (item.description || '').toLowerCase().includes(q);
    return nameMatch || catMatch || descMatch;
  });

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          <h2>{isAvailabilityOnlyView ? 'Food Availability Control' : 'Menu Management'}</h2>
          <p>
            {isAvailabilityOnlyView
              ? 'Quick kitchen toggle to instantly enable or disable food items based on stock'
              : 'Add new food items, update pricing, descriptions, and toggle stock availability'}
          </p>
        </div>
        <div className="page-actions">
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={fetchMenu}
            disabled={loading}
          >
            <RefreshCw size={15} className={loading ? 'spinner' : ''} />
            <span>Refresh</span>
          </button>
          {!isAvailabilityOnlyView && (
            <button
              type="button"
              className="btn btn-primary btn-sm"
              onClick={handleOpenAddModal}
            >
              <Plus size={15} />
              <span>Add Menu Item</span>
            </button>
          )}
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
            placeholder="Search food by name, category, or description..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="filter-group">
          {categories.map((cat) => (
            <button
              key={cat}
              type="button"
              className={`filter-chip ${selectedCategory === cat ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat)}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Menu Table / Cards */}
      {loading ? (
        <div className="state-box">
          <div className="spinner"></div>
          <p>Loading menu items...</p>
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="card-container">
          <div className="state-box">
            <UtensilsCrossed />
            <h4>No menu items found</h4>
            <p>
              {searchQuery
                ? `No items match "${searchQuery}"`
                : selectedCategory !== 'All'
                ? `No items found in category "${selectedCategory}"`
                : 'The menu is currently empty. Click "Add Menu Item" to get started.'}
            </p>
            {!isAvailabilityOnlyView && (
              <button
                type="button"
                className="btn btn-primary btn-sm"
                onClick={handleOpenAddModal}
                style={{ marginTop: '0.5rem' }}
              >
                <Plus size={15} />
                <span>Add First Item</span>
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="card-container">
          <div className="table-responsive">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Item Details</th>
                  <th>Category</th>
                  <th>Price</th>
                  <th>Availability State</th>
                  <th>Quick Toggle</th>
                  {!isAvailabilityOnlyView && <th style={{ textAlign: 'right' }}>Actions</th>}
                </tr>
              </thead>
              <tbody>
                {filteredItems.map((item) => {
                  const isToggling = togglingId === item.id;

                  return (
                    <tr key={item.id}>
                      <td>
                        <div style={{ fontWeight: 600, color: 'var(--color-text)', fontSize: '0.95rem' }}>
                          {item.name}
                        </div>
                        {item.description && (
                          <div
                            style={{
                              fontSize: '0.8rem',
                              color: 'var(--color-text-dim)',
                              maxWidth: 380,
                              whiteSpace: 'normal',
                              marginTop: 2,
                            }}
                          >
                            {item.description}
                          </div>
                        )}
                      </td>
                      <td>
                        <span
                          style={{
                            padding: '0.2rem 0.6rem',
                            borderRadius: 'var(--radius-full)',
                            background: 'rgba(255, 255, 255, 0.06)',
                            fontSize: '0.8rem',
                            color: 'var(--color-text-muted)',
                          }}
                        >
                          {item.category}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontWeight: 700, color: 'var(--color-primary)' }}>
                          ₹{Number(item.price).toFixed(2)}
                        </span>
                      </td>
                      <td>
                        <AvailabilityBadge isAvailable={item.is_available} />
                      </td>
                      <td>
                        <button
                          type="button"
                          className={`btn btn-sm ${item.is_available ? 'btn-danger-outline' : 'btn-success'}`}
                          onClick={() => handleToggleAvailability(item)}
                          disabled={isToggling}
                          title={
                            item.is_available
                              ? 'Click to disable item availability'
                              : 'Click to enable item availability'
                          }
                        >
                          {item.is_available ? (
                            <>
                              <ToggleLeft size={14} />
                              <span>Disable</span>
                            </>
                          ) : (
                            <>
                              <ToggleRight size={14} />
                              <span>Enable</span>
                            </>
                          )}
                        </button>
                      </td>
                      {!isAvailabilityOnlyView && (
                        <td style={{ textAlign: 'right' }}>
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.4rem' }}>
                            <button
                              type="button"
                              className="btn btn-secondary btn-icon"
                              onClick={() => handleOpenEditModal(item)}
                              title="Edit item details"
                            >
                              <Edit2 size={14} />
                            </button>
                            <button
                              type="button"
                              className="btn btn-danger-outline btn-icon"
                              onClick={() => handleOpenDeleteModal(item)}
                              title="Delete item"
                            >
                              <Trash2 size={14} />
                            </button>
                          </div>
                        </td>
                      )}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Add / Edit Menu Item Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => !submitting && setModalOpen(false)}
        title={editingItem ? 'Edit Menu Item' : 'Add New Menu Item'}
        footer={
          <>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setModalOpen(false)}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleSaveItem}
              disabled={submitting}
            >
              {submitting ? (
                <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }}></span>
              ) : (
                <>
                  <Check size={16} />
                  <span>{editingItem ? 'Update Item' : 'Create Item'}</span>
                </>
              )}
            </button>
          </>
        }
      >
        <form onSubmit={handleSaveItem} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="form-group">
            <label className="form-label">
              Item Name <span className="req">*</span>
            </label>
            <input
              type="text"
              className="form-control"
              placeholder="e.g. Masala Dosa, Cold Coffee"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              autoFocus
            />
            {formErrors.name && (
              <span style={{ color: 'var(--color-danger)', fontSize: '0.78rem' }}>
                {formErrors.name}
              </span>
            )}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">
                Price (₹) <span className="req">*</span>
              </label>
              <input
                type="number"
                step="0.5"
                min="0"
                className="form-control"
                placeholder="e.g. 60.00"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
              />
              {formErrors.price && (
                <span style={{ color: 'var(--color-danger)', fontSize: '0.78rem' }}>
                  {formErrors.price}
                </span>
              )}
            </div>

            <div className="form-group">
              <label className="form-label">
                Category <span className="req">*</span>
              </label>
              <select
                className="form-control"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              >
                <option value="Breakfast">Breakfast</option>
                <option value="Lunch">Lunch</option>
                <option value="Snacks">Snacks</option>
                <option value="Beverages">Beverages</option>
                <option value="Desserts">Desserts</option>
                <option value="General">General</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea
              className="form-control"
              rows={2}
              placeholder="Brief description of the dish, ingredients, or taste profile"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            ></textarea>
          </div>

          <div className="form-group">
            <label className="form-label">Image URL (Optional)</label>
            <input
              type="url"
              className="form-control"
              placeholder="https://example.com/item.jpg"
              value={formData.image_url}
              onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
            />
          </div>

          <div className="toggle-switch-wrap">
            <div>
              <div style={{ fontWeight: 600, color: 'var(--color-text)', fontSize: '0.9rem' }}>
                Availability Status
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--color-text-dim)' }}>
                {formData.is_available
                  ? 'Item is currently in-stock and visible to customers'
                  : 'Item is out-of-stock and disabled for ordering'}
              </div>
            </div>
            <button
              type="button"
              className={`btn btn-sm ${formData.is_available ? 'btn-success' : 'btn-danger-outline'}`}
              onClick={() => setFormData({ ...formData, is_available: !formData.is_available })}
            >
              {formData.is_available ? 'Available' : 'Unavailable'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteModalOpen}
        onClose={() => !deleting && setDeleteModalOpen(false)}
        title="Confirm Menu Item Removal"
        footer={
          <>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setDeleteModalOpen(false)}
              disabled={deleting}
            >
              Cancel
            </button>
            <button
              type="button"
              className="btn btn-danger"
              onClick={handleDeleteItem}
              disabled={deleting}
            >
              {deleting ? (
                <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }}></span>
              ) : (
                <>
                  <Trash2 size={16} />
                  <span>Remove Item</span>
                </>
              )}
            </button>
          </>
        }
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: 'var(--color-danger)' }}>
            <AlertTriangle size={24} />
            <span style={{ fontWeight: 600, fontSize: '1rem' }}>
              Are you sure you want to delete this menu item?
            </span>
          </div>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>
            You are about to remove <strong>"{itemToDelete?.name}"</strong> from the canteen menu.
            This action cannot be undone.
          </p>
        </div>
      </Modal>
    </div>
  );
}
