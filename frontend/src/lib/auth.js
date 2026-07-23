// Auth utilities for TEKOSECURE
// Uses Supabase JWT tokens

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
