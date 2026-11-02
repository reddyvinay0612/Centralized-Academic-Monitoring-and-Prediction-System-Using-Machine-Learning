import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '@/services/api';
import { INITIAL_USERS } from '@/mocks/data';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(() => {
    const saved = localStorage.getItem('camps_user');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        // Fall back to null or default
      }
    }
    return INITIAL_USERS[0]; // Admin by default for initial review
  });

  const [accessToken, setAccessToken] = useState(() => {
    return localStorage.getItem('camps_access_token') || null;
  });

  const [mustChangePassword, setMustChangePassword] = useState(false);

  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('camps_theme') === 'dark';
  });

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('camps_theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('camps_theme', 'light');
    }
  }, [darkMode]);

  const toggleDarkMode = () => setDarkMode((prev) => !prev);

  // Real API Login with Role Verification
  const login = async (identifier, password, expectedRole) => {
    try {
      const response = await api.post('/auth/login', {
        identifier,
        password,
        expectedRole,
      });

      if (response.data?.success) {
        const { user, access_token, claims, redirectTo, mustChangePassword: needsPwdChange } = response.data;
        setCurrentUser(user);
        setAccessToken(access_token);
        setMustChangePassword(Boolean(needsPwdChange));

        localStorage.setItem('camps_user', JSON.stringify(user));
        localStorage.setItem('camps_access_token', access_token);

        return { success: true, user, redirectTo, mustChangePassword: needsPwdChange };
      }
      return { success: false, message: response.data?.message || 'Login failed' };
    } catch (error) {
      const errorData = error.response?.data;
      // If backend is running and rejected (e.g. ROLE_MISMATCH, INVALID_CREDENTIALS, ACCOUNT_LOCKED)
      if (errorData) {
        return {
          success: false,
          error: errorData.error,
          message: errorData.message || 'Authentication error',
        };
      }

      // Offline Staging Fallback if backend API is not yet running
      console.warn('Backend server not reachable, utilizing local fallback authentication for preview.');
      const matched = INITIAL_USERS.find(
        (u) =>
          u.email.toLowerCase() === identifier.toLowerCase() ||
          u.username.toLowerCase() === identifier.toLowerCase() ||
          u.usn?.toLowerCase() === identifier.toLowerCase()
      ) || INITIAL_USERS[0];

      if (expectedRole && matched.role !== expectedRole) {
        return {
          success: false,
          error: 'ROLE_MISMATCH',
          message: `These credentials are not for a ${expectedRole} account. Please use the appropriate portal.`,
        };
      }

      setCurrentUser(matched);
      localStorage.setItem('camps_user', JSON.stringify(matched));
      return {
        success: true,
        user: matched,
        redirectTo: `/${matched.role}/dashboard`,
      };
    }
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (e) {
      // Ignore network errors on logout
    } finally {
      setCurrentUser(null);
      setAccessToken(null);
      localStorage.removeItem('camps_user');
      localStorage.removeItem('camps_access_token');
    }
  };

  const switchRole = (role) => {
    const user = INITIAL_USERS.find((u) => u.role === role) || INITIAL_USERS[0];
    setCurrentUser(user);
    localStorage.setItem('camps_user', JSON.stringify(user));
  };

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        setCurrentUser,
        accessToken,
        login,
        logout,
        switchRole,
        darkMode,
        toggleDarkMode,
        mustChangePassword,
        setMustChangePassword,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
