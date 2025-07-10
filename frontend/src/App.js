import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import UserManagement from './components/UserManagement';
import Analytics from './components/Analytics';
import DatabaseTools from './components/DatabaseTools';
import EmergencyRecovery from './components/EmergencyRecovery';
import Navigation from './components/Navigation';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Toaster position="top-right" />
          <AppContent />
        </div>
      </Router>
    </AuthProvider>
  );
}

function AppContent() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <Routes>
      {/* Emergency Recovery Route - Always accessible */}
      <Route path="/emergency-recovery" element={<EmergencyRecovery />} />
      
      {/* Protected Routes - Require authentication */}
      {!user ? (
        <Route path="*" element={<Login />} />
      ) : (
        <>
          <Route path="/" element={
            <div className="flex">
              <Navigation />
              <main className="flex-1 ml-64 p-8">
                <Dashboard />
              </main>
            </div>
          } />
          <Route path="/dashboard" element={
            <div className="flex">
              <Navigation />
              <main className="flex-1 ml-64 p-8">
                <Dashboard />
              </main>
            </div>
          } />
          <Route path="/users" element={
            <div className="flex">
              <Navigation />
              <main className="flex-1 ml-64 p-8">
                <UserManagement />
              </main>
            </div>
          } />
          <Route path="/analytics" element={
            <div className="flex">
              <Navigation />
              <main className="flex-1 ml-64 p-8">
                <Analytics />
              </main>
            </div>
          } />
          <Route path="/database" element={
            <div className="flex">
              <Navigation />
              <main className="flex-1 ml-64 p-8">
                <DatabaseTools />
              </main>
            </div>
          } />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </>
      )}
    </Routes>
  );
}

export default App;
