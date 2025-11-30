import React, { createContext, useState, useContext, useEffect } from 'react';
import { login as apiLogin } from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('auditflow_token'));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (token) {
      // In a real app, we would validate the token with the backend here via /users/me
      // For now, we assume it's valid if present
      setUser({ email: 'user@authenticated.com' }); // Placeholder
    }
  }, [token]);

  const login = async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiLogin(email, password);
      setToken(data.access_token);
      localStorage.setItem('auditflow_token', data.access_token);
      setUser({ email });
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
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading, error }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
