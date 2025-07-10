import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';

const Login = () => {
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [showDemo, setShowDemo] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const result = await login(formData.email, formData.password);
      
      if (result.success) {
        toast.success(`Welcome back, ${result.user.first_name}!`);
      } else {
        toast.error(result.message);
      }
    } catch (error) {
      toast.error('An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = async (role) => {
    const demoCredentials = {
      admin: { email: 'admin@example.com', password: 'admin123' },
      staff: { email: 'staff@example.com', password: 'staff123' },
      customer: { email: 'customer@example.com', password: 'customer123' }
    };

    const credentials = demoCredentials[role];
    setFormData(credentials);
    
    setIsLoading(true);
    try {
      const result = await login(credentials.email, credentials.password);
      
      if (result.success) {
        toast.success(`Demo login successful as ${role}!`);
      } else {
        toast.error(result.message);
      }
    } catch (error) {
      toast.error('Demo login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 via-blue-800 to-purple-800">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="mx-auto h-12 w-12 bg-blue-600 rounded-full flex items-center justify-center mb-4">
              <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h2 className="text-3xl font-bold text-gray-900">E-Commerce Admin</h2>
            <p className="mt-2 text-gray-600">Database Administration Portal</p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="form-label">
                Email Address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                className="input-field"
                placeholder="Enter your email"
                value={formData.email}
                onChange={handleChange}
              />
            </div>

            <div>
              <label htmlFor="password" className="form-label">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="input-field"
                placeholder="Enter your password"
                value={formData.password}
                onChange={handleChange}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className={`w-full btn-primary ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <div className="spinner h-5 w-5 mr-2"></div>
                  Signing in...
                </div>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Demo Accounts */}
          <div className="mt-8">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Demo Accounts</span>
              </div>
            </div>

            <div className="mt-6">
              <button
                type="button"
                onClick={() => setShowDemo(!showDemo)}
                className="w-full text-center text-blue-600 hover:text-blue-800 font-medium"
              >
                {showDemo ? 'Hide' : 'Show'} Demo Credentials
              </button>

              {showDemo && (
                <div className="mt-4 space-y-3 fade-in">
                  <div className="grid grid-cols-3 gap-2">
                    <button
                      onClick={() => handleDemoLogin('admin')}
                      disabled={isLoading}
                      className="btn-primary text-xs py-2 px-3"
                    >
                      Admin Demo
                    </button>
                    <button
                      onClick={() => handleDemoLogin('staff')}
                      disabled={isLoading}
                      className="btn-secondary text-xs py-2 px-3"
                    >
                      Staff Demo
                    </button>
                    <button
                      onClick={() => handleDemoLogin('customer')}
                      disabled={isLoading}
                      className="btn-success text-xs py-2 px-3"
                    >
                      Customer Demo
                    </button>
                  </div>
                  <div className="text-xs text-gray-500 text-center">
                    Click any button above to login with demo credentials
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Features */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Platform Features</h3>
            <div className="grid grid-cols-2 gap-3 text-xs text-gray-600">
              <div className="flex items-center">
                <div className="h-2 w-2 bg-green-400 rounded-full mr-2"></div>
                User Management
              </div>
              <div className="flex items-center">
                <div className="h-2 w-2 bg-blue-400 rounded-full mr-2"></div>
                Role-Based Access
              </div>
              <div className="flex items-center">
                <div className="h-2 w-2 bg-purple-400 rounded-full mr-2"></div>
                Performance Analytics
              </div>
              <div className="flex items-center">
                <div className="h-2 w-2 bg-orange-400 rounded-full mr-2"></div>
                Database Backup
              </div>
            </div>
          </div>

          {/* Emergency Recovery Link */}
          <div className="mt-6 pt-4 border-t border-gray-200">
            <div className="text-center">
              <Link 
                to="/emergency-recovery"
                className="inline-flex items-center text-red-600 hover:text-red-800 text-sm font-medium transition-colors"
              >
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                🚨 Emergency Database Recovery
              </Link>
              <p className="text-xs text-gray-500 mt-1">
                Access when database is unavailable
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-white text-sm opacity-80">
          Database Administration Project © 2024
        </div>
      </div>
    </div>
  );
};

export default Login;
