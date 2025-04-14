import React, { createContext, useState, useEffect, useContext } from 'react';
import PropTypes from 'prop-types';

// Create authentication context
const AuthContext = createContext(null);

/**
 * AuthProvider component that manages authentication state and provides
 * authentication-related functionality to child components.
 */
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check for existing authentication on component mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Check if we have a token in local storage
        const token = localStorage.getItem('auth_token');
        if (!token) {
          setLoading(false);
          return;
        }

        // Verify token with the backend
        const response = await fetch('/api/auth/verify', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        } else {
          // Token is invalid, remove it
          localStorage.removeItem('auth_token');
        }
      } catch (err) {
        console.error('Authentication error:', err);
        setError('Failed to verify authentication');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  /**
   * Log in a user
   * @param {string} usernameOrEmail - Username or email
   * @param {string} password - Password
   * @returns {Promise<Object>} Login result
   */
  const login = async (usernameOrEmail, password) => {
    setError(null);
    setLoading(true);

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username_or_email: usernameOrEmail, password })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Login failed');
      }

      // Store token in local storage
      localStorage.setItem('auth_token', data.token);
      
      // Update user state
      setUser({
        id: data.user_id,
        username: data.username,
        email: data.email
      });

      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Register a new user
   * @param {string} username - Username
   * @param {string} email - Email
   * @param {string} password - Password
   * @returns {Promise<Object>} Registration result
   */
  const register = async (username, email, password) => {
    setError(null);
    setLoading(true);

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, email, password })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Registration failed');
      }

      // Store token in local storage
      localStorage.setItem('auth_token', data.token);
      
      // Update user state
      setUser({
        id: data.user_id,
        username: data.username,
        email: data.email
      });

      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Log out the current user
   */
  const logout = () => {
    // Remove token from local storage
    localStorage.removeItem('auth_token');
    
    // Clear user state
    setUser(null);
  };

  /**
   * Get the authentication token
   * @returns {string|null} The authentication token or null if not logged in
   */
  const getToken = () => {
    return localStorage.getItem('auth_token');
  };

  /**
   * Get the authenticated fetch function for API requests
   * @returns {Function} Authenticated fetch function
   */
  const authFetch = async (url, options = {}) => {
    const token = getToken();
    
    if (!token) {
      throw new Error('Authentication required');
    }

    const authOptions = {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`
      }
    };

    const response = await fetch(url, authOptions);
    
    // If we get a 401 Unauthorized, the token may be invalid or expired
    if (response.status === 401) {
      logout();
      throw new Error('Session expired. Please log in again.');
    }
    
    return response;
  };

  // Create the context value
  const contextValue = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    getToken,
    authFetch,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

AuthProvider.propTypes = {
  children: PropTypes.node.isRequired
};

/**
 * Custom hook to use the auth context
 * @returns {Object} Auth context
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthProvider;