import React, { useState } from 'react';
import { Shield, ShieldAlert, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '../lib/auth';

export default function LoginPage() {
  const { signIn, signUp } = useAuth();
  const [mode, setMode] = useState('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function onSubmit(e) {
    e.preventDefault();
    setError('');
    setBusy(true);
    const fn = mode === 'signin' ? signIn : signUp;
    const { error } = await fn(email, password);
    setBusy(false);
    if (error) {
      setError(error.message);
      return;
    }
    if (mode === 'signup') {
      toast.success('Cuenta creada. Verifica tu email si el proyecto lo exige.');
    }
  }

  return (
    <div className="min-h-screen relative flex items-center justify-center p-6 overflow-hidden">
      {/* Ambient grid */}
      <div
        className="absolute inset-0 opacity-40 pointer-events-none"
        style={{
          backgroundImage:
            'linear-gradient(rgba(30,58,138,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(30,58,138,0.08) 1px, transparent 1px)',
          backgroundSize: '48px 48px',
          maskImage:
            'radial-gradient(ellipse at center, black 40%, transparent 80%)',
        }}
      />
      <div className="absolute top-8 left-8 flex items-center gap-3 mono text-xs tracking-widest text-ink-dim">
        <div className="dot bg-neon-on shadow-glow-on animate-pulseGlow" />
        <span>TEKOSECURE // SOC v1.0</span>
      </div>
      <div className="absolute top-8 right-8 mono text-[11px] tracking-widest text-ink-muted">
        {new Date().toISOString().replace('T', ' ').slice(0, 19)} UTC
      </div>

      <form
        onSubmit={onSubmit}
        data-testid="login-form"
        className="relative panel w-full max-w-md p-8 shadow-[0_0_60px_rgba(0,191,255,0.08)]"
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="w-11 h-11 rounded-md border border-neon-cyan/40 bg-neon-cyan/10 flex items-center justify-center shadow-glow-cyan">
            <Shield className="w-6 h-6 text-neon-cyan" strokeWidth={1.6} />
          </div>
          <div>
            <div className="mono text-[10px] tracking-[0.28em] text-ink-muted">
              SECURE ACCESS
            </div>
            <h1 className="text-2xl font-semibold tracking-tight">
              Panel de Operaciones
            </h1>
          </div>
        </div>

        <p className="text-ink-dim text-[13px] mb-6 leading-relaxed">
          {mode === 'signin'
            ? 'Autentícate para ver alertas, estado de NVRs y actividad en tiempo real.'
            : 'Crea una cuenta operativa para acceder al centro de control.'}
        </p>

        <label className="block mb-4">
          <span className="mono text-[10px] tracking-[0.2em] text-ink-muted">
            EMAIL
          </span>
          <input
            data-testid="login-email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full bg-bg-950/70 border border-line/60 rounded px-3 py-2.5 mono text-sm text-ink focus:outline-none focus:border-neon-cyan/60 focus:shadow-glow-cyan transition"
            placeholder="operador@tekosecure.io"
          />
        </label>

        <label className="block mb-6">
          <span className="mono text-[10px] tracking-[0.2em] text-ink-muted">
            PASSWORD
          </span>
          <input
            data-testid="login-password"
            type="password"
            required
            minLength={6}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full bg-bg-950/70 border border-line/60 rounded px-3 py-2.5 mono text-sm text-ink focus:outline-none focus:border-neon-cyan/60 focus:shadow-glow-cyan transition"
            placeholder="••••••••"
          />
        </label>

        {error && (
          <div
            data-testid="login-error"
            className="flex items-start gap-2 mb-4 p-3 rounded border border-neon-crit/40 bg-neon-crit/10 text-neon-crit mono text-[12px]"
          >
            <AlertCircle className="w-4 h-4 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <button
          data-testid="login-submit"
          type="submit"
          disabled={busy}
          className="w-full mono tracking-widest text-[12px] uppercase bg-neon-cyan/15 hover:bg-neon-cyan/25 border border-neon-cyan/50 text-neon-cyan py-3 rounded transition shadow-glow-cyan disabled:opacity-60"
        >
          {busy ? 'Autenticando...' : mode === 'signin' ? '// Iniciar Sesión' : '// Registrar'}
        </button>

        <button
          type="button"
          onClick={() => {
            setError('');
            setMode(mode === 'signin' ? 'signup' : 'signin');
          }}
          className="mt-4 w-full mono text-[11px] tracking-widest text-ink-dim hover:text-neon-cyan transition"
          data-testid="login-toggle-mode"
        >
          {mode === 'signin'
            ? '¿Sin cuenta? Registrar operador →'
            : '← Ya tengo cuenta, iniciar sesión'}
        </button>

        <div className="mt-8 pt-6 border-t border-line/40 flex items-center gap-2 text-ink-muted mono text-[10px] tracking-widest">
          <ShieldAlert className="w-3.5 h-3.5" />
          <span>ACCESO REGISTRADO Y AUDITADO</span>
        </div>
      </form>
    </div>
  );
}
