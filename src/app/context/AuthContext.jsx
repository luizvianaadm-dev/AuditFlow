import React, { createContext, useState, useContext, useEffect } from 'react';
import { login as apiLogin } from '../services/authService';

const API_URL = import.meta.env.VITE_API_URL || 'https://auditflow-api.railway.app';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('auditflow_token'));
  const [loading, setLoading] = useState(true); // Start with loading=true for initial token verification
  const [error, setError] = useState(null);
  const [authInitialized, setAuthInitialized] = useState(false); // Track if we've tried to verify token

  useEffect(() => {
    const verifyToken = async () => {
      if (token && !authInitialized) {
        setLoading(true);
        try {
          // Fetch user profile from backend
          const res = await fetch(`${API_URL}/users/me`, {
            headers: { 'Authorization': `Bearer ${token}` },
          });
          
          if (res.ok) {
            const data = await res.json();
            setUser(data);
          } else {
            // Token invalid or expired
            logout();
          }
        } catch (err) {
          // Network error - keep the token for now, but don't set user
          // This prevents automatic logout on network failures
          console.warn('Failed to verify token:', err);
          setError('Verifying session...');
        } finally {
          setLoading(false);
          setAuthInitialized(true);
        }
      } else if (!token) {
        setLoading(false);
        setAuthInitialized(true);
      }
    };

    verifyToken();
  }, [token, authInitialized]);

  const login = async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiLogin(email, password);
      setToken(data.access_token);
      localStorage.setItem('auditflow_token', data.access_token);
      setUser({ email });
      setAuthInitialized(false); // Reset to allow re-verification with new token
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('auditflow_token');
    setAuthInitialized(false);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading, error }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
