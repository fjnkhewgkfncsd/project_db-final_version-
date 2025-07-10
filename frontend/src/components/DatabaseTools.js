import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

const DatabaseTools = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('query');
  const [queryText, setQueryText] = useState('');
  const [queryResults, setQueryResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [backupStatus, setBackupStatus] = useState(null);
  const [restoreStatus, setRestoreStatus] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [backupFiles, setBackupFiles] = useState([]);
  const [backupType, setBackupType] = useState('complete');
  const [performanceData, setPerformanceData] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);

  // Sample predefined queries for different roles
  const predefinedQueries = {
    admin: [
      {
        name: 'User Statistics',
        query: 'SELECT role, COUNT(*) as count, AVG(EXTRACT(DAYS FROM (NOW() - created_at))) as avg_days_registered FROM users GROUP BY role;'
      },
      {
        name: 'Top Categories by Products',
        query: 'SELECT c.name, COUNT(p.product_id) as product_count FROM categories c LEFT JOIN products p ON c.category_id = p.category_id GROUP BY c.category_id, c.name ORDER BY product_count DESC LIMIT 10;'
      },
      {
        name: 'Product Inventory Status',
        query: 'SELECT name, sku, stock_quantity, base_price FROM products WHERE stock_quantity < 10 ORDER BY stock_quantity ASC LIMIT 20;'
      },
      {
        name: 'Recent User Registrations',
        query: 'SELECT username, email, role, created_at FROM users ORDER BY created_at DESC LIMIT 10;'
      }
    ],
    staff: [
      {
        name: 'Recent Orders',
        query: 'SELECT order_id, user_id, order_status, total_amount, created_at FROM orders ORDER BY created_at DESC LIMIT 20;'
      },
      {
        name: 'Products by Category',
        query: 'SELECT c.name as category, COUNT(p.product_id) as product_count FROM categories c LEFT JOIN products p ON c.category_id = p.category_id GROUP BY c.name ORDER BY product_count DESC;'
      },
      {
        name: 'User Activity',
        query: 'SELECT role, COUNT(*) as total_users, COUNT(*) FILTER (WHERE last_login > NOW() - INTERVAL \'30 days\') as active_users FROM users GROUP BY role;'
      }
    ],
    read_only: [
      {
        name: 'Product Catalog',
        query: 'SELECT p.name, p.base_price, c.name as category, p.stock_quantity FROM products p JOIN categories c ON p.category_id = c.category_id ORDER BY p.name LIMIT 50;'
      },
      {
        name: 'Category List',
        query: 'SELECT name, description, is_active FROM categories ORDER BY name;'
      },
      {
        name: 'System Tables',
        query: 'SELECT table_name, table_type FROM information_schema.tables WHERE table_schema = \'public\' ORDER BY table_name;'
      }
    ]
  };

  useEffect(() => {
    if (activeTab === 'performance' || activeTab === 'monitoring') {
      fetchPerformanceData();
      if (activeTab === 'monitoring') {
        fetchSystemStatus();
      }
    }
  }, [activeTab]);

  const fetchPerformanceData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/analytics/system-performance', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();
      if (data.success) {
        setPerformanceData(data.data);
      }
    } catch (error) {
      console.error('Failed to fetch performance data:', error);
    }
  };

  const fetchSystemStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/analytics/system-status', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();
      if (data.success) {
        setSystemStatus(data.data);
      }
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    }
  };

  const executeQuery = async () => {
    if (!queryText.trim()) return;

    setLoading(true);
    console.log('🔍 Executing query:', queryText);
    try {
      const token = localStorage.getItem('token');
      console.log('🔑 Token available:', !!token);
      
      const response = await fetch('/api/database/execute-query', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: queryText })
      });

      console.log('📡 Response status:', response.status);
      console.log('📡 Response ok:', response.ok);
      
      const data = await response.json();
      console.log('📊 Response data:', data);

      if (data.success) {
        console.log('✅ Query successful, setting results:', {
          rows: data.data.rows,
          rowCount: data.data.row_count,
          executionTime: data.data.execution_time_ms
        });
        setQueryResults({
          success: true,
          rows: data.data.rows,
          rowCount: data.data.row_count,
          executionTime: `${data.data.execution_time_ms}ms`
        });
      } else {
        console.log('❌ Query failed:', data.message);
        setQueryResults({
          success: false,
          error: data.message
        });
      }
    } catch (error) {
      console.log('💥 Exception caught:', error);
      setQueryResults({
        success: false,
        error: error.message
      });
    } finally {
      console.log('🏁 Query execution finished, setting loading to false');
      setLoading(false);
    }
  };

  const performBackup = async () => {
    setLoading(true);
    setBackupStatus('Connecting to database...');
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/database/backup', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ backupType })
      });

      const data = await response.json();

      if (data.success) {
        setBackupStatus(`✅ Backup completed successfully!
        📄 File: ${data.data.filename}
        📊 Size: ${data.data.size}
        🕒 Created: ${new Date(data.data.timestamp).toLocaleString()}
        📋 Tables: ${data.data.tables_backed_up.length} tables backed up`);
        
        // Refresh backup files list
        fetchBackupFiles();
      } else {
        setBackupStatus(`❌ Backup failed: ${data.message}`);
      }
    } catch (error) {
      setBackupStatus(`❌ Backup failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const performRestore = async (filename) => {
    setLoading(true);
    setRestoreStatus('Starting restore...');
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/database/restore', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ filename: filename })
      });
      const data = await response.json();
      if (data.success) {
        setRestoreStatus(`✅ Database restored successfully!
        📄 File: ${data.data.filename}
        verification: ${data.data.verification.userCount}
        🕒 Restored at: ${new Date(data.data.restored_at).toLocaleString()}
        ⏱️ Execution time: ${data.data.execution_time_ms}ms`);
      } else {
        setRestoreStatus(`❌ Restore failed: ${data.message}`);
      }
    } catch (error) {
      setRestoreStatus(`❌ Restore failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleFileRestore = () => {
    if (!selectedFile) {
      setRestoreStatus('❌ Please select a backup file first');
      return;
    }
    performRestore(selectedFile.name);
  };

  const fetchBackupFiles = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/database/backups', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        const backupFiles = data.data?.backups || [];
        setBackupFiles(backupFiles);
      }
    } catch (error) {
      console.error('Error fetching backup files:', error);
    }
  };

  useEffect(() => {
    fetchBackupFiles();
  }, []);

  const tabs = [
    { id: 'query', name: 'Query Console', icon: '🔍' },
    { id: 'backup', name: 'Backup & Restore', icon: '💾' },
    { id: 'performance', name: 'Performance', icon: '⚡' },
    { id: 'monitoring', name: 'Monitoring', icon: '📊' }
  ];

  const userQueries = predefinedQueries[user?.role] || predefinedQueries.read_only;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Database Tools</h1>
        <div className="text-sm text-gray-500">
          Role: <span className="font-medium capitalize">{user?.role || 'guest'}</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Query Console Tab */}
      {activeTab === 'query' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">SQL Query Console</h3>
            
            {/* Predefined Queries */}
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Quick Queries:</h4>
              <div className="flex flex-wrap gap-2">
                {userQueries.map((query, index) => (
                  <button
                    key={index}
                    onClick={() => setQueryText(query.query)}
                    className="px-3 py-1 text-sm bg-blue-100 text-blue-800 rounded-md hover:bg-blue-200 transition-colors"
                  >
                    {query.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Query Input */}
            <div className="mb-4">
              <textarea
                value={queryText}
                onChange={(e) => setQueryText(e.target.value)}
                placeholder="Enter your SQL query here..."
                className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
              />
            </div>

            <button
              onClick={executeQuery}
              disabled={loading || !queryText.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Executing...' : 'Execute Query'}
            </button>

            {/* Query Results */}
            {queryResults && (
              <div className="mt-6">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Results:</h4>
                {queryResults.success ? (
                  <div>
                    <div className="mb-2 text-sm text-gray-600">
                      {queryResults.rowCount} rows returned in {queryResults.executionTime}
                    </div>
                    <div className="overflow-x-auto">
                      <table className="min-w-full border border-gray-300">
                        <thead className="bg-gray-50">
                          <tr>
                            {queryResults.rows.length > 0 && Object.keys(queryResults.rows[0]).map((key) => (
                              <th key={key} className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                {key}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {queryResults.rows.map((row, index) => (
                            <tr key={index}>
                              {Object.values(row).map((value, i) => (
                                <td key={i} className="px-4 py-2 text-sm text-gray-900">
                                  {value}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ) : (
                  <div className="text-red-600 text-sm">
                    Error: {queryResults.error}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Backup & Restore Tab */}
      {activeTab === 'backup' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Database Backup</h3>
            <p className="text-sm text-gray-600 mb-4">
              Create a backup of the database. Choose backup type based on your needs.
            </p>
            
            {/* Backup Type Selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Backup Type:</label>
              <select
                value={backupType}
                onChange={(e) => setBackupType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="complete">🔄 Complete (Schema + Data)</option>
                <option value="schema-only">🏗️ Schema Only (Structure)</option>
                <option value="data-only">📊 Data Only (Records)</option>
              </select>
              <div className="mt-2 text-xs text-gray-500">
                {backupType === 'complete' && '• Full database backup including tables, data, indexes, and constraints'}
                {backupType === 'schema-only' && '• Only database structure (tables, indexes, constraints) without data'}
                {backupType === 'data-only' && '• Only table data without structure (requires existing schema)'}
              </div>
            </div>
            
            <button
              onClick={performBackup}
              disabled={loading}
              className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? 'Creating Backup...' : `Create ${backupType === 'complete' ? 'Complete' : backupType === 'schema-only' ? 'Schema' : 'Data'} Backup`}
            </button>
            {backupStatus && (
              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                <p className="text-sm text-blue-800 whitespace-pre-line">{backupStatus}</p>
              </div>
            )}
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Database Restore</h3>
            <p className="text-sm text-gray-600 mb-4">
              Restore database from a backup file. This will overwrite current data.
            </p>
            
            {/* Available Backup Files */}
            {backupFiles.length > 0 && (
              <div className="mb-6">
                <h4 className="text-md font-medium text-gray-800 mb-3">Available Backup Files:</h4>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {backupFiles.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{file.filename}</p>
                        <p className="text-xs text-gray-500">
                          Size: {file.size} | Created: {new Date(file.created).toLocaleString()}
                        </p>
                      </div>
                      <button
                        onClick={() => performRestore(file.filename)}
                        disabled={loading}
                        className="ml-3 px-3 py-1 bg-orange-600 text-white text-sm rounded-md hover:bg-orange-700 disabled:opacity-50"
                      >
                        Restore
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* File Upload for Custom Restore */}
            <div className="border-t pt-4">
              <h4 className="text-md font-medium text-gray-800 mb-3">Upload Custom Backup File:</h4>
              <input
                type="file"
                accept=".sql,.dump"
                onChange={(e) => setSelectedFile(e.target.files[0])}
                className="mb-4 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
              <button
                onClick={handleFileRestore}
                disabled={loading || !selectedFile}
                className="w-full px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 disabled:opacity-50"
              >
                {loading ? 'Restoring...' : 'Restore from Uploaded File'}
              </button>
            </div>
            
            {restoreStatus && (
              <div className="mt-4 p-3 bg-orange-50 border border-orange-200 rounded-md">
                <p className="text-sm text-orange-800 whitespace-pre-line">{restoreStatus}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Performance Tab */}
      {activeTab === 'performance' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-6">Database Performance Metrics</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{performanceData?.database_response_time || 'N/A'}</div>
              <div className="text-sm text-gray-600">Avg Query Time</div>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold text-green-600">{performanceData?.uptime_hours ? `${performanceData.uptime_hours}h` : 'N/A'}</div>
              <div className="text-sm text-gray-600">Uptime</div>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{performanceData?.queries_per_hour || 'N/A'}</div>
              <div className="text-sm text-gray-600">Queries/Hour</div>
            </div>
          </div>

          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">Recent Query Performance</h4>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Query
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Execution Time
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Rows Affected
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {performanceData?.recent_queries && performanceData.recent_queries.length > 0 ? (
                    performanceData.recent_queries.map((query, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 text-sm text-gray-900 font-mono max-w-xs truncate">
                          {query.query}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {query.duration}ms
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {query.rowCount}
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            query.status === 'Fast' ? 'bg-green-100 text-green-800' :
                            query.status === 'Moderate' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {query.status}
                          </span>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="4" className="px-6 py-4 text-sm text-gray-500 text-center">
                        No recent queries to display. Execute some queries to see performance data.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Monitoring Tab */}
      {activeTab === 'monitoring' && (
        <div className="space-y-6">
          {/* System Health Overview */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-medium text-gray-900">System Health Overview</h3>
              <button
                onClick={() => {
                  fetchPerformanceData();
                  fetchSystemStatus();
                }}
                className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Refresh
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {systemStatus?.database_status === 'online' ? '🟢' : '🔴'} 
                  {systemStatus?.database_status || 'Unknown'}
                </div>
                <div className="text-sm text-gray-600">Database Status</div>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {systemStatus?.api_status === 'running' ? '🟢' : '🔴'} 
                  {systemStatus?.api_status || 'Unknown'}
                </div>
                <div className="text-sm text-gray-600">API Status</div>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {systemStatus?.backup_status === 'active' ? '🟢' : '🟡'} 
                  {systemStatus?.backup_status || 'Unknown'}
                </div>
                <div className="text-sm text-gray-600">Backup Status</div>
              </div>
            </div>
          </div>

          {/* Real-time Metrics */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-6">Real-time Metrics</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Database Connections</h4>
                <div className="space-y-2">
                  {performanceData?.connection_breakdown ? (
                    performanceData.connection_breakdown.map((conn, index) => (
                      <div key={index} className="flex justify-between">
                        <span className="text-sm text-gray-600 capitalize">
                          {conn.state || 'Unknown'}
                        </span>
                        <span className="text-sm font-medium">{conn.count}</span>
                      </div>
                    ))
                  ) : (
                    <>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Active</span>
                        <span className="text-sm font-medium">{performanceData?.active_connections || '5'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Idle</span>
                        <span className="text-sm font-medium">12</span>
                      </div>
                    </>
                  )}
                </div>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-3">System Resources</h4>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm">
                      <span>Response Time</span>
                      <span>{performanceData?.database_response_time || '45ms'}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-blue-600 h-2 rounded-full" style={{
                        width: performanceData?.database_response_time ? 
                          `${Math.min(100, Math.max(10, parseInt(performanceData.database_response_time) / 2))}%` : 
                          '45%'
                      }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm">
                      <span>Memory Usage</span>
                      <span>{performanceData?.memory_usage || '67%'}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-green-600 h-2 rounded-full" style={{width: performanceData?.memory_usage || '67%'}}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm">
                      <span>API Success Rate</span>
                      <span>{performanceData?.api_success_rate || '98%'}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-yellow-600 h-2 rounded-full" style={{width: performanceData?.api_success_rate || '98%'}}></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* System Information */}
          {systemStatus && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-6">System Information</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Server Details</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Node.js Version</span>
                      <span className="text-sm font-medium">{systemStatus.node_version || 'Unknown'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">System Uptime</span>
                      <span className="text-sm font-medium">
                        {systemStatus.system_uptime ? 
                          `${Math.floor(systemStatus.system_uptime / 3600)}h ${Math.floor((systemStatus.system_uptime % 3600) / 60)}m` : 
                          'Unknown'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Last Backup</span>
                      <span className="text-sm font-medium">{systemStatus.last_backup || 'Never'}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Memory Usage</h4>
                  <div className="space-y-2">
                    {systemStatus.memory_usage && (
                      <>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Used Memory</span>
                          <span className="text-sm font-medium">
                            {Math.round(systemStatus.memory_usage.heapUsed / 1024 / 1024)}MB
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Total Heap</span>
                          <span className="text-sm font-medium">
                            {Math.round(systemStatus.memory_usage.heapTotal / 1024 / 1024)}MB
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">External Memory</span>
                          <span className="text-sm font-medium">
                            {Math.round(systemStatus.memory_usage.external / 1024 / 1024)}MB
                          </span>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Recent Activity */}
          {systemStatus?.recent_activities && systemStatus.recent_activities.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-6">Recent Activity</h3>
              
              <div className="space-y-3">
                {systemStatus.recent_activities.map((activity, index) => (
                  <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                    <div className="text-lg">
                      {activity.icon === 'user' ? '👤' : '📊'}
                    </div>
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-900">{activity.type}</div>
                      <div className="text-sm text-gray-500">{activity.description}</div>
                    </div>
                    <div className="text-xs text-gray-400">
                      {new Date(activity.time).toLocaleTimeString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Database Tables */}
          {performanceData?.largest_tables && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-6">Largest Tables</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Table Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Size
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {performanceData.largest_tables.map((table, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 text-sm text-gray-900">{table.table_name}</td>
                        <td className="px-6 py-4 text-sm text-gray-500">{table.size}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DatabaseTools;
