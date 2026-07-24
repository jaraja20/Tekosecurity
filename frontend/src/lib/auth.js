import React, { useEffect, useState, createContext, useContext } from 'react';
import { supabase } from './supabase';

const AuthContext = createContext(null);

// Sign in function
export async function signIn(email, password) {
  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) return { error };

    // Store token
    if (data.session) {
      localStorage.setItem('auth_token', data.session.access_token);
    }

    return { data };
  } catch (err) {
    return { error: err };
  }
}

// Sign up function
export async function signUp(email, password) {
  try {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    });

    if (error) return { error };

    // Store token if immediately confirmed
    if (data.session) {
      localStorage.setItem('auth_token', data.session.access_token);
    }

    return { data };
  } catch (err) {
    return { error: err };
  }
}

// Sign out function
export async function signOut() {
  localStorage.removeItem('auth_token');
  return await supabase.auth.signOut();
}

// Get auth token
export async function getAuthToken() {
  const token = localStorage.getItem('auth_token');
  return token;
}

export function setAuthToken(token) {
  localStorage.setItem('auth_token', token);
}

export function clearAuthToken() {
  localStorage.removeItem('auth_token');
}

export function isAuthenticated() {
  return !!getAuthToken();
}

// React hook for auth
export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function checkAuth() {
      try {
        const {
          data: { user },
        } = await supabase.auth.getUser();
        setUser(user);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    }

    checkAuth();

    // Subscribe to auth changes
    const { data: listener } = supabase.auth.onAuthStateChange((event, session) => {
      setUser(session?.user || null);
      if (session?.access_token) {
        setAuthToken(session.access_token);
      } else {
        clearAuthToken();
      }
    });

    return () => {
      listener?.subscription?.unsubscribe();
    };
  }, []);

  return {
    user,
    session: user,
    loading,
    error,
    signIn,
    signUp,
    signOut
  };
}

// Auth Provider Component
export function AuthProvider({ children }) {
  const auth = useAuth();

  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>;
}

// Hook to use auth context
export function useAuthContext() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext debe usarse dentro de AuthProvider');
  }
  return context;
}
