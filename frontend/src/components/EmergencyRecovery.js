import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './EmergencyRecovery.css';

const EmergencyRecovery = () => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [credentials, setCredentials] = useState({ username: '', password: '' });
    const [backups, setBackups] = useState([]);
    const [selectedBackup, setSelectedBackup] = useState('');
    const [dbStatus, setDbStatus] = useState(null);
    const [loading, setLoading] = useState(false);
    const [logs, setLogs] = useState([]);
    const [message, setMessage] = useState('');

    const API_BASE = 'http://localhost:3002/api/emergency';

    // Set up axios interceptor for authentication
    useEffect(() => {
        const token = localStorage.getItem('emergency_token');
        if (token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            setIsAuthenticated(true);
            loadInitialData();
        }
    }, []);

    const loadInitialData = async () => {
        await checkDatabaseStatus();
        await loadBackups();
        await loadLogs();
    };

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage('');

        try {
            const response = await axios.post(`${API_BASE}/login`, credentials);
            
            if (response.data.success) {
                const token = response.data.data.token;
                localStorage.setItem('emergency_token', token);
                axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
                setIsAuthenticated(true);
                setMessage('Emergency authentication successful');
                await loadInitialData();
            }
        } catch (error) {
            setMessage(error.response?.data?.message || 'Authentication failed');
        } finally {
            setLoading(false);
        }
    };

    const checkDatabaseStatus = async () => {
        try {
            const response = await axios.get(`${API_BASE}/database-status`);
            setDbStatus(response.data.data);
        } catch (error) {
            console.error('Failed to check database status:', error);
        }
    };

    const loadBackups = async () => {
        try {
            const response = await axios.get(`${API_BASE}/backups`);
            setBackups(response.data.data.backups);
        } catch (error) {
            setMessage('Failed to load backup files');
        }
    };

    const loadLogs = async () => {
        try {
            const response = await axios.get(`${API_BASE}/logs`);
            setLogs(response.data.data.logs);
        } catch (error) {
            console.error('Failed to load logs:', error);
        }
    };

    const handleRestore = async () => {
        if (!selectedBackup) {
            setMessage('Please select a backup file');
            return;
        }

        const confirmMessage = `⚠️ WARNING: This will restore the database from backup "${selectedBackup}". This action cannot be undone. Continue?`;
        
        if (!window.confirm(confirmMessage)) {
            return;
        }

        setLoading(true);
        setMessage('Starting database restoration... Please wait.');

        try {
            const response = await axios.post(`${API_BASE}/restore`, {
                filename: selectedBackup,
                force: true
            });

            if (response.data.success) {
                setMessage(`✅ Database restored successfully from ${selectedBackup}`);
                await checkDatabaseStatus();
                await loadLogs();
            }
        } catch (error) {
            setMessage(`❌ Restore failed: ${error.response?.data?.message || error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const formatFileSize = (bytes) => {
        return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleString();
    };

    const logout = () => {
        localStorage.removeItem('emergency_token');
        delete axios.defaults.headers.common['Authorization'];
        setIsAuthenticated(false);
        setCredentials({ username: '', password: '' });
    };

    if (!isAuthenticated) {
        return (
            <div className="emergency-recovery">
                <div className="emergency-header">
                    <h1>🚨 Emergency Database Recovery</h1>
                    <p>This system operates independently when the main database is unavailable</p>
                </div>

                <div className="login-container">
                    <div className="login-form">
                        <h2>🔐 Emergency Authentication Required</h2>
                        <p>Enter emergency credentials to access database recovery tools</p>
                        
                        <form onSubmit={handleLogin}>
                            <div className="form-group">
                                <label htmlFor="username">Username:</label>
                                <input
                                    type="text"
                                    id="username"
                                    value={credentials.username}
                                    onChange={(e) => setCredentials({...credentials, username: e.target.value})}
                                    required
                                    autoComplete="username"
                                />
                            </div>
                            
                            <div className="form-group">
                                <label htmlFor="password">Password:</label>
                                <input
                                    type="password"
                                    id="password"
                                    value={credentials.password}
                                    onChange={(e) => setCredentials({...credentials, password: e.target.value})}
                                    required
                                    autoComplete="current-password"
                                />
                            </div>
                            
                            <button type="submit" disabled={loading}>
                                {loading ? 'Authenticating...' : 'Login'}
                            </button>
                        </form>
                        
                        {message && <div className={`message ${message.includes('successful') ? 'success' : 'error'}`}>{message}</div>}
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="emergency-recovery">
            <div className="emergency-header">
                <h1>🚨 Emergency Database Recovery System</h1>
                <div className="header-actions">
                    <button onClick={checkDatabaseStatus} className="btn-secondary">
                        🔄 Check DB Status
                    </button>
                    <button onClick={logout} className="btn-danger">
                        🚪 Logout
                    </button>
                </div>
            </div>

            {/* Database Status */}
            <div className="status-section">
                <h2>📊 Database Status</h2>
                {dbStatus && (
                    <div className={`status-card ${dbStatus.status}`}>
                        <div className="status-indicator">
                            {dbStatus.status === 'online' ? '🟢' : '🔴'}
                        </div>
                        <div className="status-info">
                            <strong>Status:</strong> {dbStatus.status.toUpperCase()}<br/>
                            <strong>Message:</strong> {dbStatus.message}
                            {dbStatus.error && <><br/><strong>Error:</strong> {dbStatus.error}</>}
                        </div>
                    </div>
                )}
            </div>

            {/* Backup Selection */}
            <div className="backup-section">
                <h2>📁 Available Backup Files</h2>
                <div className="backup-selection">
                    {backups.length > 0 ? (
                        <div className="backup-list">
                            {backups.map((backup, index) => (
                                <div 
                                    key={backup.filename}
                                    className={`backup-item ${selectedBackup === backup.filename ? 'selected' : ''}`}
                                    onClick={() => setSelectedBackup(backup.filename)}
                                >
                                    <div className="backup-info">
                                        <div className="backup-name">{backup.filename}</div>
                                        <div className="backup-details">
                                            <span className="backup-type">{backup.type.toUpperCase()}</span>
                                            <span className="backup-size">{backup.sizeFormatted}</span>
                                            <span className="backup-date">{formatDate(backup.modified)}</span>
                                        </div>
                                    </div>
                                    <div className="backup-select">
                                        <input 
                                            type="radio" 
                                            name="selectedBackup" 
                                            value={backup.filename}
                                            checked={selectedBackup === backup.filename}
                                            onChange={() => setSelectedBackup(backup.filename)}
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="no-backups">No backup files found</div>
                    )}
                </div>
            </div>

            {/* Restore Actions */}
            <div className="actions-section">
                <h2>⚡ Recovery Actions</h2>
                <div className="action-buttons">
                    <button 
                        onClick={handleRestore}
                        disabled={!selectedBackup || loading}
                        className="btn-primary restore-btn"
                    >
                        {loading ? '🔄 Restoring...' : '🔧 Restore Database'}
                    </button>
                    <button onClick={loadBackups} className="btn-secondary">
                        🔄 Refresh Backups
                    </button>
                </div>
                
                {selectedBackup && (
                    <div className="selected-backup-info">
                        <strong>Selected backup:</strong> {selectedBackup}
                    </div>
                )}
            </div>

            {/* Messages */}
            {message && (
                <div className="message-section">
                    <div className={`message ${message.includes('✅') ? 'success' : message.includes('❌') ? 'error' : 'info'}`}>
                        {message}
                    </div>
                </div>
            )}

            {/* Recovery Logs */}
            <div className="logs-section">
                <h2>📝 Recovery Logs</h2>
                <div className="logs-container">
                    {logs.length > 0 ? (
                        <div className="logs-list">
                            {logs.slice(0, 20).map((log, index) => (
                                <div key={index} className="log-entry">
                                    {log}
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="no-logs">No recovery logs available</div>
                    )}
                </div>
                <button onClick={loadLogs} className="btn-secondary">
                    🔄 Refresh Logs
                </button>
            </div>
        </div>
    );
};

export default EmergencyRecovery;
