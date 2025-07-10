import React, { useState, useEffect } from 'react';
import axios from 'axios';

const EmergencyRecoveryWidget = () => {
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        checkEmergencySystemStatus();
        // Check every 30 seconds
        const interval = setInterval(checkEmergencySystemStatus, 30000);
        return () => clearInterval(interval);
    }, []);

    const checkEmergencySystemStatus = async () => {
        try {
            // Check if emergency recovery server is running
            const response = await axios.get('http://localhost:3002/health', {
                timeout: 3000
            });
            
            if (response.data.success) {
                setStatus('available');
            } else {
                setStatus('unavailable');
            }
        } catch (error) {
            setStatus('unavailable');
        } finally {
            setLoading(false);
        }
    };

    const getStatusIcon = () => {
        if (loading) return '⏳';
        switch (status) {
            case 'available': return '🟢';
            case 'unavailable': return '🔴';
            default: return '❓';
        }
    };

    const getStatusText = () => {
        if (loading) return 'Checking...';
        switch (status) {
            case 'available': return 'Ready';
            case 'unavailable': return 'Offline';
            default: return 'Unknown';
        }
    };

    const getStatusColor = () => {
        switch (status) {
            case 'available': return 'text-green-600';
            case 'unavailable': return 'text-red-600';
            default: return 'text-gray-600';
        }
    };

    return (
        <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-red-500">
            <div className="flex items-center justify-between">
                <div>
                    <h3 className="text-sm font-medium text-gray-900">Emergency Recovery</h3>
                    <p className="text-xs text-gray-500 mt-1">Database disaster recovery system</p>
                </div>
                <div className="text-right">
                    <div className="flex items-center space-x-2">
                        <span className="text-lg">{getStatusIcon()}</span>
                        <span className={`text-sm font-medium ${getStatusColor()}`}>
                            {getStatusText()}
                        </span>
                    </div>
                </div>
            </div>
            
            <div className="mt-3 flex space-x-2">
                <a
                    href="/emergency-recovery"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-3 py-1 border border-red-300 shadow-sm text-xs font-medium rounded text-red-700 bg-red-50 hover:bg-red-100 transition-colors"
                >
                    <svg className="h-3 w-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                    Access Recovery
                </a>
                
                <button
                    onClick={checkEmergencySystemStatus}
                    disabled={loading}
                    className="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 transition-colors"
                >
                    <svg className="h-3 w-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Refresh
                </button>
            </div>

            {status === 'unavailable' && (
                <div className="mt-2 p-2 bg-red-50 rounded text-xs text-red-700">
                    <strong>⚠️ Emergency recovery system is offline!</strong>
                    <br />
                    To enable: Run "Start Emergency Recovery Server" task
                </div>
            )}
        </div>
    );
};

export default EmergencyRecoveryWidget;
