import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { useAuth } from './AuthProvider';

/**
 * Login form component for user authentication
 */
const LoginForm = ({ onSuccess, redirectUrl }) => {
  const { login, loading, error } = useAuth();
  const [usernameOrEmail, setUsernameOrEmail] = useState('');
  const [password, setPassword] = useState('');
  const [formError, setFormError] = useState('');

  /**
   * Handle form submission
   * @param {Event} e - Form event
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');

    // Basic validation
    if (!usernameOrEmail.trim()) {
      setFormError('Please enter your username or email');
      return;
    }
    
    if (!password) {
      setFormError('Please enter your password');
      return;
    }

    try {
      await login(usernameOrEmail, password);
      
      // Call the success callback or redirect
      if (onSuccess) {
        onSuccess();
      } else if (redirectUrl) {
        window.location.href = redirectUrl;
      }
    } catch (err) {
      setFormError(err.message || 'Login failed');
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <form 
        onSubmit={handleSubmit} 
        className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4"
      >
        <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Log In</h2>
        
        {/* Error message */}
        {(formError || error) && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {formError || error}
          </div>
        )}
        
        {/* Username/Email field */}
        <div className="mb-4">
          <label 
            className="block text-gray-700 text-sm font-bold mb-2" 
            htmlFor="usernameOrEmail"
          >
            Username or Email
          </label>
          <input
            id="usernameOrEmail"
            type="text"
            value={usernameOrEmail}
            onChange={(e) => setUsernameOrEmail(e.target.value)}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            placeholder="Enter your username or email"
            disabled={loading}
          />
        </div>
        
        {/* Password field */}
        <div className="mb-6">
          <label 
            className="block text-gray-700 text-sm font-bold mb-2" 
            htmlFor="password"
          >
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
            placeholder="Enter your password"
            disabled={loading}
          />
        </div>
        
        {/* Submit button */}
        <div className="flex items-center justify-between">
          <button
            type="submit"
            className={`bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full ${
              loading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </div>
      </form>
      
      <p className="text-center text-gray-600 text-sm">
        Don't have an account? <a href="/register" className="text-blue-500 hover:text-blue-700">Register here</a>
      </p>
    </div>
  );
};

LoginForm.propTypes = {
  onSuccess: PropTypes.func,
  redirectUrl: PropTypes.string
};

export default LoginForm;