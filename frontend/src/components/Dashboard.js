import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import EmergencyRecoveryWidget from './EmergencyRecoveryWidget';

const Dashboard = () => {
  const { user, isAdmin, isStaff } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [actionStatus, setActionStatus] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('token');
      const headers = { 'Authorization': `Bearer ${token}` };

      // Fetch user statistics if admin/staff
      const promises = [];
      
      if (isAdmin || isStaff) {
        promises.push(axios.get('/api/users/stats', { headers }));
      }
      
      // Fetch system status for all users
      promises.push(axios.get('/api/analytics/system-status', { headers }));
      
      // Fetch performance metrics for admin/staff
      if (isAdmin || isStaff) {
        promises.push(axios.get('/api/analytics/system-performance', { headers }));
      }

      const results = await Promise.all(promises);
      
      let resultIndex = 0;
      
      if (isAdmin || isStaff) {
        const userStatsResponse = results[resultIndex++];
        if (userStatsResponse.data.success) {
          setStats(userStatsResponse.data.data.stats);
        }
      }
      
      const statusResponse = results[resultIndex++];
      if (statusResponse.data.success) {
        setSystemStatus(statusResponse.data.data);
      }
      
      if (isAdmin || isStaff) {
        const perfResponse = results[resultIndex++];
        if (perfResponse.data.success) {
          setPerformance(perfResponse.data.data);
        }
      }

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      
      // Handle rate limiting specifically
      if (error.response?.status === 429) {
        setError('Rate limit exceeded. Please wait a moment before refreshing.');
      } else {
        setError(error.response?.data?.message || 'Failed to load dashboard data');
      }
    } finally {
      setLoading(false);
    }
  }, [isAdmin, isStaff]);

  useEffect(() => {
    fetchDashboardData();
    // Only set up auto-refresh if enabled
    if (autoRefresh) {
      // Refresh system data every 2 minutes instead of 30 seconds to avoid rate limiting
      const interval = setInterval(fetchDashboardData, 120000);
      return () => clearInterval(interval);
    }
  }, [fetchDashboardData, autoRefresh]);

  // Quick action handlers
  const handleCreateUser = () => {
    navigate('/users');
  };

  const handleDatabaseBackup = async () => {
    setActionLoading(true);
    setActionStatus('Creating backup...');
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('/api/database/backup', {}, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.data.success) {
        setActionStatus('✅ Backup created successfully!');
        setTimeout(() => setActionStatus(null), 3000);
      }
    } catch (error) {
      setActionStatus('❌ Backup failed: ' + (error.response?.data?.message || error.message));
      setTimeout(() => setActionStatus(null), 5000);
    } finally {
      setActionLoading(false);
    }
  };

  const handleSystemReports = () => {
    navigate('/analytics');
  };

  const handlePerformanceAnalytics = () => {
    navigate('/database');
  };

  const handleManageOrders = () => {
    // Navigate to orders management (you may need to create this route)
    setActionStatus('📦 Orders management coming soon!');
    setTimeout(() => setActionStatus(null), 3000);
  };

  const handleViewReports = () => {
    navigate('/analytics');
  };

  const handleViewProfile = () => {
    setActionStatus('👤 Profile management coming soon!');
    setTimeout(() => setActionStatus(null), 3000);
  };

  const handleUpdateSettings = () => {
    setActionStatus('⚙️ Settings management coming soon!');
    setTimeout(() => setActionStatus(null), 3000);
  };

  const StatCard = ({ title, value, icon, color = 'blue', subtitle }) => (
    <div className="card">
      <div className="flex items-center">
        <div className={`p-3 rounded-full bg-${color}-100 mr-4`}>
          <div className={`h-6 w-6 text-${color}-600`}>
            {icon}
          </div>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500">{subtitle}</p>
          )}
        </div>
      </div>
    </div>
  );

  const QuickActions = () => (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
      
      {/* Action Status Display */}
      {actionStatus && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-sm text-blue-800">{actionStatus}</p>
        </div>
      )}
      
      <div className="grid grid-cols-2 gap-3">
        {isAdmin && (
          <>
            <button 
              onClick={handleCreateUser}
              disabled={actionLoading}
              className="btn-primary text-sm disabled:opacity-50"
            >
              👥 Create User
            </button>
            <button 
              onClick={handleDatabaseBackup}
              disabled={actionLoading}
              className="btn-secondary text-sm disabled:opacity-50"
            >
              {actionLoading ? '⏳ Backing up...' : '💾 Database Backup'}
            </button>
            <button 
              onClick={handleSystemReports}
              disabled={actionLoading}
              className="btn-secondary text-sm disabled:opacity-50"
            >
              📊 System Reports
            </button>
            <button 
              onClick={handlePerformanceAnalytics}
              disabled={actionLoading}
              className="btn-secondary text-sm disabled:opacity-50"
            >
              ⚡ Performance Analytics
            </button>
          </>
        )}
        {isStaff && !isAdmin && (
          <>
            <button 
              onClick={handleManageOrders}
              disabled={actionLoading}
              className="btn-primary text-sm disabled:opacity-50"
            >
              📦 Manage Orders
            </button>
            <button 
              onClick={handleViewReports}
              disabled={actionLoading}
              className="btn-secondary text-sm disabled:opacity-50"
            >
              📈 View Reports
            </button>
          </>
        )}
        {!isAdmin && !isStaff && (
          <>
            <button 
              onClick={handleViewProfile}
              disabled={actionLoading}
              className="btn-primary text-sm disabled:opacity-50"
            >
              👤 View Profile
            </button>
            <button 
              onClick={handleUpdateSettings}
              disabled={actionLoading}
              className="btn-secondary text-sm disabled:opacity-50"
            >
              ⚙️ Update Settings
            </button>
          </>
        )}
      </div>
    </div>
  );

  const SystemStatus = () => (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Database</span>
          <span className={`flex items-center ${systemStatus?.database_status === 'online' ? 'text-green-600' : 'text-red-600'}`}>
            <div className={`h-2 w-2 ${systemStatus?.database_status === 'online' ? 'bg-green-400' : 'bg-red-400'} rounded-full mr-2`}></div>
            {systemStatus?.database_status === 'online' ? 'Online' : 'Offline'}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">API Services</span>
          <span className={`flex items-center ${systemStatus?.api_status === 'running' ? 'text-green-600' : 'text-red-600'}`}>
            <div className={`h-2 w-2 ${systemStatus?.api_status === 'running' ? 'bg-green-400' : 'bg-red-400'} rounded-full mr-2`}></div>
            {systemStatus?.api_status === 'running' ? 'Running' : 'Stopped'}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Backup System</span>
          <span className={`flex items-center ${systemStatus?.backup_status === 'active' ? 'text-green-600' : 'text-yellow-600'}`}>
            <div className={`h-2 w-2 ${systemStatus?.backup_status === 'active' ? 'bg-green-400' : 'bg-yellow-400'} rounded-full mr-2`}></div>
            {systemStatus?.backup_status === 'active' ? 'Active' : 'Inactive'}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Last Backup</span>
          <span className="text-sm text-gray-900">{systemStatus?.last_backup || 'Unknown'}</span>
        </div>
      </div>
    </div>
  );

  const RecentActivity = () => (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
      <div className="space-y-3">
        {systemStatus?.recent_activities?.length > 0 ? (
          systemStatus.recent_activities.map((activity, index) => (
            <div key={index} className="flex items-start space-x-3">
              <div className={`h-2 w-2 ${
                activity.icon === 'user' ? 'bg-green-400' : 
                activity.icon === 'backup' ? 'bg-blue-400' : 'bg-yellow-400'
              } rounded-full mt-2`}></div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">{activity.description}</p>
                <p className="text-xs text-gray-500">
                  {new Date(activity.time).toLocaleString()}
                </p>
              </div>
            </div>
          ))
        ) : (
          <>
            <div className="flex items-start space-x-3">
              <div className="h-2 w-2 bg-blue-400 rounded-full mt-2"></div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">System started successfully</p>
                <p className="text-xs text-gray-500">
                  {systemStatus?.timestamp ? new Date(systemStatus.timestamp).toLocaleString() : 'Recently'}
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="h-2 w-2 bg-green-400 rounded-full mt-2"></div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">Database connection established</p>
                <p className="text-xs text-gray-500">System startup</p>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );

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
          <h3 className="text-lg font-medium text-gray-900">Error Loading Dashboard</h3>
          <p className="text-gray-500 mt-1">{error}</p>
          <button 
            onClick={fetchDashboardData}
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
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">
            Welcome back, {user?.first_name}! Here's what's happening with your system.
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <button
              onClick={fetchDashboardData}
              disabled={loading}
              className="btn-secondary text-sm disabled:opacity-50"
            >
              {loading ? '🔄 Refreshing...' : '🔄 Refresh'}
            </button>
            <label className="flex items-center text-sm text-gray-600">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="mr-2"
              />
              Auto-refresh (2min)
            </label>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">
              {new Date().toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </p>
          </div>
        </div>
      </div>

      {/* Stats Grid - Admin/Staff Only */}
      {(isAdmin || isStaff) && stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Users"
            value={stats.total_users?.toLocaleString() || '0'}
            icon={
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
              </svg>
            }
            color="blue"
          />
          <StatCard
            title="Active Users"
            value={stats.active_users?.toLocaleString() || '0'}
            icon={
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
            color="green"
          />
          <StatCard
            title="New Users (30d)"
            value={stats.new_users_last_30_days?.toLocaleString() || '0'}
            icon={
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
              </svg>
            }
            color="purple"
          />
          <StatCard
            title="Active Last 7d"
            value={stats.active_last_7_days?.toLocaleString() || '0'}
            icon={
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            }
            color="yellow"
          />
        </div>
      )}

      {/* Role Breakdown - Admin Only */}
      {isAdmin && stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatCard
            title="Administrators"
            value={stats.admin_count?.toLocaleString() || '0'}
            icon={
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            }
            color="purple"
          />
          <StatCard
            title="Staff Members"
            value={stats.staff_count?.toLocaleString() || '0'}
            icon={
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            }
            color="blue"
          />
          <StatCard
            title="Customers"
            value={stats.customer_count?.toLocaleString() || '0'}
            icon={
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            }
            color="green"
          />
        </div>
      )}

      {/* Action Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <QuickActions />
        <SystemStatus />
        {/* Emergency Recovery Widget - Admin Only */}
        {isAdmin && <EmergencyRecoveryWidget />}
      </div>

      {/* Activity and Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentActivity />
        
        {/* Performance Overview */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Overview</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Database Response Time</span>
                <span className="text-gray-900">{performance?.database_response_time || '12ms'} avg</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ 
                  width: performance?.database_response_time ? 
                    `${Math.max(10, Math.min(100, 100 - (parseInt(performance.database_response_time) / 2)))}%` : 
                    '85%' 
                }}></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">API Success Rate</span>
                <span className="text-gray-900">{performance?.api_success_rate || '99.2%'}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{ 
                  width: performance?.api_success_rate ? 
                    performance.api_success_rate : 
                    '99%' 
                }}></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Memory Usage</span>
                <span className="text-gray-900">{performance?.memory_usage || '68%'}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-yellow-600 h-2 rounded-full" style={{ 
                  width: performance?.memory_usage || '68%' 
                }}></div>
              </div>
            </div>
            
            {performance && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Active Connections:</span>
                    <span className="ml-2 font-medium">{performance.active_connections}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Queries/Hour:</span>
                    <span className="ml-2 font-medium">{performance.queries_per_hour?.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">DB Size:</span>
                    <span className="ml-2 font-medium">{performance.database_size}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Uptime:</span>
                    <span className="ml-2 font-medium">{performance.uptime_hours}h</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
