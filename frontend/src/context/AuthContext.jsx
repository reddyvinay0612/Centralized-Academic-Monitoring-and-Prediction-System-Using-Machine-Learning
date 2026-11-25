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
      const cleanId = (identifier || '').trim().toLowerCase();
      let matched = INITIAL_USERS.find(
        (u) =>
          (u.email && u.email.toLowerCase() === cleanId) ||
          (u.username && u.username.toLowerCase() === cleanId) ||
          (u.usn && u.usn.toLowerCase() === cleanId)
      );

      // Auto-synthesize student or parent session for valid college USNs during offline preview
      if (!matched && expectedRole === 'student' && /^4pm/i.test(cleanId)) {
        matched = {
          id: 999,
          name: cleanId.toUpperCase(),
          username: cleanId.toUpperCase(),
          usn: cleanId.toUpperCase(),
          email: `${cleanId.toLowerCase()}@pesitm.edu`,
          role: 'student',
          active: true,
          department: 'Engineering'
        };
      } else if (!matched && expectedRole === 'parent' && (/^4pm/i.test(cleanId) || cleanId.includes('parent'))) {
        matched = {
          id: 998,
          name: `Parent of ${cleanId.toUpperCase()}`,
          username: cleanId.toLowerCase(),
          email: `${cleanId.toLowerCase()}@parent.pesitm.edu`,
          role: 'parent',
          active: true,
          studentUsn: cleanId.replace('parent_', '').toUpperCase()
        };
      }

      if (!matched) {
        return {
          success: false,
          error: 'SERVER_UNREACHABLE',
          message: 'Backend server is temporarily starting up. Please retry in 5 seconds.',
        };
      }

      if (expectedRole && matched.role !== expectedRole) {
        const isHodTeacherMatch =
          (expectedRole === 'teacher' && matched.role === 'hod') ||
          (expectedRole === 'hod' && (matched.role === 'hod' || matched.role === 'teacher'));

        if (!isHodTeacherMatch) {
          return {
            success: false,
            error: 'ROLE_MISMATCH',
            message: `These credentials are not for a ${expectedRole} account. Please use the appropriate portal.`,
          };
        }
      }

      const devToken = `offline_dev_token_${matched.role}_${matched.username || matched.email || 'user'}`;
      setCurrentUser(matched);
      setAccessToken(devToken);
      localStorage.setItem('camps_user', JSON.stringify(matched));
      localStorage.setItem('camps_access_token', devToken);
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
        user: currentUser,
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
