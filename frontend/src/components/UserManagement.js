import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import toast from 'react-hot-toast';

const UserManagement = () => {
  const { isAdmin } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({});
  const [filters, setFilters] = useState({
    page: 1,
    limit: 20,
    search: '',
    role: ''
  });
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams(filters);
      const response = await axios.get(`/api/users?${params}`);

      if (response.data.success) {
        setUsers(response.data.data.users);
        setPagination(response.data.data.pagination);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
      setError(error.response?.data?.message || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleSearch = (e) => {
    setFilters(prev => ({
      ...prev,
      search: e.target.value,
      page: 1
    }));
  };

  const handleRoleFilter = (e) => {
    setFilters(prev => ({
      ...prev,
      role: e.target.value,
      page: 1
    }));
  };

  const handlePageChange = (newPage) => {
    setFilters(prev => ({
      ...prev,
      page: newPage
    }));
  };

  const handleEditUser = (user) => {
    setEditingUser(user);
    setShowCreateModal(true);
  };

  const handleDeactivateUser = async (userId) => {
    if (!window.confirm('Are you sure you want to deactivate this user?')) {
      return;
    }

    try {
      const response = await axios.patch(`/api/users/${userId}/deactivate`);
      
      if (response.data.success) {
        toast.success('User deactivated successfully');
        fetchUsers();
      }
    } catch (error) {
      console.error('Error deactivating user:', error);
      toast.error(error.response?.data?.message || 'Failed to deactivate user');
    }
  };

  const UserTable = () => (
    <div className="table-container">
      <table className="table">
        <thead>
          <tr className="bg-gray-50">
            <th className="table-header">Name</th>
            <th className="table-header">Email</th>
            <th className="table-header">Role</th>
            <th className="table-header">Status</th>
            <th className="table-header">Created</th>
            <th className="table-header">Last Login</th>
            {isAdmin && <th className="table-header">Actions</th>}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {users.map((user) => (
            <tr key={user.user_id} className="hover:bg-gray-50">
              <td className="table-cell">
                <div className="flex items-center">
                  <div className="h-8 w-8 bg-blue-600 rounded-full flex items-center justify-center mr-3">
                    <span className="text-white text-xs font-medium">
                      {user.first_name?.[0]}{user.last_name?.[0]}
                    </span>
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">
                      {user.first_name} {user.last_name}
                    </div>
                    <div className="text-gray-500 text-sm">@{user.username}</div>
                  </div>
                </div>
              </td>
              <td className="table-cell">
                <div className="text-gray-900">{user.email}</div>
              </td>
              <td className="table-cell">
                <span className={`badge ${
                  user.role === 'admin' ? 'badge-admin' :
                  user.role === 'staff' ? 'badge-staff' : 'badge-customer'
                }`}>
                  {user.role}
                </span>
              </td>
              <td className="table-cell">
                <span className={`badge ${
                  user.is_active ? 'badge-active' : 'badge-inactive'
                }`}>
                  {user.is_active ? 'Active' : 'Inactive'}
                </span>
              </td>
              <td className="table-cell text-gray-500">
                {new Date(user.created_at).toLocaleDateString()}
              </td>
              <td className="table-cell text-gray-500">
                {user.last_login ? 
                  new Date(user.last_login).toLocaleDateString() : 
                  'Never'
                }
              </td>
              {isAdmin && (
                <td className="table-cell">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleEditUser(user)}
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                    >
                      Edit
                    </button>
                    {user.is_active && user.user_id !== user?.user_id && (
                      <button
                        onClick={() => handleDeactivateUser(user.user_id)}
                        className="text-red-600 hover:text-red-800 text-sm font-medium"
                      >
                        Deactivate
                      </button>
                    )}
                  </div>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const Pagination = () => {
    if (!pagination.totalPages || pagination.totalPages <= 1) return null;

    return (
      <div className="flex items-center justify-between px-6 py-3 bg-white border-t border-gray-200">
        <div className="text-sm text-gray-700">
          Showing {((pagination.currentPage - 1) * filters.limit) + 1} to{' '}
          {Math.min(pagination.currentPage * filters.limit, pagination.totalUsers)} of{' '}
          {pagination.totalUsers} users
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => handlePageChange(pagination.currentPage - 1)}
            disabled={!pagination.hasPrevPage}
            className={`px-3 py-1 text-sm border rounded ${
              pagination.hasPrevPage
                ? 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                : 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed'
            }`}
          >
            Previous
          </button>
          <span className="px-3 py-1 text-sm text-gray-700">
            Page {pagination.currentPage} of {pagination.totalPages}
          </span>
          <button
            onClick={() => handlePageChange(pagination.currentPage + 1)}
            disabled={!pagination.hasNextPage}
            className={`px-3 py-1 text-sm border rounded ${
              pagination.hasNextPage
                ? 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                : 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed'
            }`}
          >
            Next
          </button>
        </div>
      </div>
    );
  };

  const CreateUserModal = () => {
    const [formData, setFormData] = useState({
      username: '',
      email: '',
      password: '',
      firstName: '',
      lastName: '',
      phone: '',
      role: 'customer'
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
      if (editingUser) {
        setFormData({
          username: editingUser.username || '',
          email: editingUser.email || '',
          password: '',
          firstName: editingUser.first_name || '',
          lastName: editingUser.last_name || '',
          phone: editingUser.phone || '',
          role: editingUser.role || 'customer'
        });
      } else {
        setFormData({
          username: '',
          email: '',
          password: '',
          firstName: '',
          lastName: '',
          phone: '',
          role: 'customer'
        });
      }
    }, [editingUser]);

    const handleSubmit = async (e) => {
      e.preventDefault();
      setIsSubmitting(true);

      try {
        let response;
        if (editingUser) {
          // Update user (exclude password if empty)
          const updateData = { ...formData };
          if (!updateData.password) {
            delete updateData.password;
          }
          response = await axios.put(`/api/users/${editingUser.user_id}`, updateData);
        } else {
          // Create new user
          response = await axios.post('/api/users/register', formData);
        }

        if (response.data.success) {
          toast.success(editingUser ? 'User updated successfully' : 'User created successfully');
          setShowCreateModal(false);
          setEditingUser(null);
          fetchUsers();
        }
      } catch (error) {
        console.error('Error submitting user:', error);
        toast.error(error.response?.data?.message || 'Failed to save user');
      } finally {
        setIsSubmitting(false);
      }
    };

    const handleClose = () => {
      setShowCreateModal(false);
      setEditingUser(null);
    };

    if (!showCreateModal) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-md">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {editingUser ? 'Edit User' : 'Create New User'}
          </h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="form-label">First Name</label>
                <input
                  type="text"
                  required
                  className="input-field"
                  value={formData.firstName}
                  onChange={(e) => setFormData(prev => ({ ...prev, firstName: e.target.value }))}
                />
              </div>
              <div>
                <label className="form-label">Last Name</label>
                <input
                  type="text"
                  required
                  className="input-field"
                  value={formData.lastName}
                  onChange={(e) => setFormData(prev => ({ ...prev, lastName: e.target.value }))}
                />
              </div>
            </div>

            <div>
              <label className="form-label">Username</label>
              <input
                type="text"
                required
                className="input-field"
                value={formData.username}
                onChange={(e) => setFormData(prev => ({ ...prev, username: e.target.value }))}
              />
            </div>

            <div>
              <label className="form-label">Email</label>
              <input
                type="email"
                required
                className="input-field"
                value={formData.email}
                onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              />
            </div>

            <div>
              <label className="form-label">
                Password {editingUser && '(leave blank to keep current)'}
              </label>
              <input
                type="password"
                required={!editingUser}
                className="input-field"
                value={formData.password}
                onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
              />
            </div>

            <div>
              <label className="form-label">Phone</label>
              <input
                type="tel"
                className="input-field"
                value={formData.phone}
                onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
              />
            </div>

            {isAdmin && (
              <div>
                <label className="form-label">Role</label>
                <select
                  className="input-field"
                  value={formData.role}
                  onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
                >
                  <option value="customer">Customer</option>
                  <option value="staff">Staff</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            )}

            <div className="flex space-x-3 pt-4">
              <button
                type="submit"
                disabled={isSubmitting}
                className={`btn-primary flex-1 ${isSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {isSubmitting ? 'Saving...' : (editingUser ? 'Update User' : 'Create User')}
              </button>
              <button
                type="button"
                onClick={handleClose}
                className="btn-secondary flex-1"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner h-8 w-8"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="text-center py-8">
          <div className="text-red-600 mb-2">
            <svg className="h-12 w-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900">Error Loading Users</h3>
          <p className="text-gray-500 mt-1">{error}</p>
          <button 
            onClick={fetchUsers}
            className="btn-primary mt-4"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
          <p className="text-gray-600">Manage system users and their roles</p>
        </div>
        {isAdmin && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary"
          >
            Create User
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
          <div className="flex-1">
            <label className="form-label">Search Users</label>
            <input
              type="text"
              className="input-field"
              placeholder="Search by name, email, or username..."
              value={filters.search}
              onChange={handleSearch}
            />
          </div>
          <div className="sm:w-48">
            <label className="form-label">Filter by Role</label>
            <select
              className="input-field"
              value={filters.role}
              onChange={handleRoleFilter}
            >
              <option value="">All Roles</option>
              <option value="admin">Admin</option>
              <option value="staff">Staff</option>
              <option value="customer">Customer</option>
            </select>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <UserTable />
      <Pagination />

      {/* Create/Edit User Modal */}
      <CreateUserModal />
    </div>
  );
};

export default UserManagement;
