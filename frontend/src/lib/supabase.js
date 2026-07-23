// Supabase client for TEKOSECURE

import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = process.env.REACT_APP_SUPABASE_URL || '';
const SUPABASE_ANON_KEY = process.env.REACT_APP_SUPABASE_ANON_KEY || '';

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Helper: Subscribe to realtime attacks
export function subscribeToAttacks(callback) {
  const subscription = supabase
    .channel('attacks')
    .on(
      'postgres_changes',
      { event: '*', schema: 'public', table: 'attacks' },
      (payload) => callback(payload)
    )
    .subscribe();

  return () => subscription.unsubscribe();
}

// Helper: Get current auth user
export async function getCurrentUser() {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  return user;
}

// Helper: Logout
export async function logout() {
  await supabase.auth.signOut();
  localStorage.removeItem('auth_token');
}
