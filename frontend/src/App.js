import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import { AuthProvider, useAuth } from './lib/auth';
import LoginPage from './pages/LoginPage';
import DashboardLayout from './pages/DashboardLayout';
import DashboardHome from './pages/DashboardHome';
import AlertsPage from './pages/AlertsPage';
import NvrPage from './pages/NvrPage';
import MikrotiksPage from './pages/MikrotiksPage';
import MikrotikDetailPage from './pages/MikrotikDetailPage';
import ReportsPage from './pages/ReportsPage';

function ProtectedRoute({ children }) {
  const { session, loading } = useAuth();
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen mono text-ink-dim">
        <span className="animate-pulse">Cargando sesión...</span>
      </div>
    );
  }
  if (!session) return <Navigate to="/login" replace />;
  return children;
}

function PublicOnly({ children }) {
  const { session, loading } = useAuth();
  if (loading) return null;
  if (session) return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster
          position="top-right"
          theme="dark"
          toastOptions={{
            style: {
              background: '#0f1533',
              border: '1px solid #1e3a8a',
              color: '#e0e6ed',
              fontFamily: 'Roboto Mono, monospace',
              fontSize: '13px',
            },
          }}
        />
        <Routes>
          <Route
            path="/login"
            element={
              <PublicOnly>
                <LoginPage />
              </PublicOnly>
            }
          />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<DashboardHome />} />
            <Route path="alerts" element={<AlertsPage />} />
            <Route path="nvrs" element={<NvrPage />} />
            <Route path="mikrotiks" element={<MikrotiksPage />} />
            <Route path="mikrotiks/:name" element={<MikrotikDetailPage />} />
            <Route path="reports" element={<ReportsPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
