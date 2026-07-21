import React, { useEffect, useState } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import {
  Activity,
  Bell,
  LogOut,
  Radio,
  ShieldCheck,
  Cpu,
  ShieldAlert,
} from 'lucide-react';
import { useAuth } from '../lib/auth';

const BACKEND = process.env.REACT_APP_BACKEND_URL?.replace(/\/$/, '') || '';

const NAV = [
  { to: '/', label: 'Dashboard', icon: Activity, end: true, testid: 'nav-dashboard' },
  { to: '/alerts', label: 'Alertas', icon: Bell, testid: 'nav-alerts' },
  { to: '/nvrs', label: 'NVRs', icon: Cpu, testid: 'nav-nvrs' },
];

function Clock() {
  const [t, setT] = useState(new Date());
  useEffect(() => {
    const i = setInterval(() => setT(new Date()), 1000);
    return () => clearInterval(i);
  }, []);
  return (
    <span data-testid="soc-clock" className="mono text-[11px] tracking-widest text-ink-dim">
      {t.toISOString().replace('T', ' ').slice(0, 19)} UTC
    </span>
  );
}

function ModeBadge() {
  const [mode, setMode] = useState(null);
  useEffect(() => {
    fetch(`${BACKEND}/api/health`)
      .then((r) => r.json())
      .then((d) => setMode(d.mode))
      .catch(() => setMode('OFFLINE'));
  }, []);
  if (!mode) return null;
  const dry = mode === 'DRY_RUN';
  const off = mode === 'OFFLINE';
  const color = off ? '#ff0040' : dry ? '#ff9100' : '#00ff88';
  return (
    <div
      data-testid="mode-badge"
      title={
        dry
          ? 'DRY-RUN: /api/actions/block-ip-real simula el SSH. Cambiar MIKROTIK_DRY_RUN=false on-prem.'
          : 'REAL: los bloqueos van a los Mikrotik por SSH.'
      }
      className="flex items-center gap-1.5 px-2 py-1 rounded border mono text-[10px] tracking-widest"
      style={{
        color,
        borderColor: `${color}55`,
        background: `${color}10`,
      }}
    >
      <ShieldAlert className="w-3 h-3" />
      MODE: {mode}
    </div>
  );
}

export default function DashboardLayout() {
  const { user, signOut } = useAuth();
  const location = useLocation();

  const title =
    location.pathname === '/'
      ? 'Panel de Operaciones'
      : location.pathname.includes('alerts')
      ? 'Alertas'
      : location.pathname.includes('nvrs')
      ? 'NVRs Hikvision'
      : 'TEKOSECURE';

  return (
    <div className="min-h-screen flex flex-col relative">
      <header className="relative z-10 flex items-center justify-between px-5 md:px-8 py-3 border-b border-line/40 bg-bg-900/80 backdrop-blur">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-md border border-neon-cyan/40 bg-neon-cyan/10 flex items-center justify-center shadow-glow-cyan">
            <ShieldCheck className="w-5 h-5 text-neon-cyan" strokeWidth={1.6} />
          </div>
          <div>
            <div className="mono text-[10px] tracking-[0.28em] text-ink-muted leading-none">
              TEKOSECURE // SOC
            </div>
            <div className="text-[15px] font-semibold tracking-tight leading-tight" data-testid="page-title">
              {title}
            </div>
          </div>
        </div>

        <div className="hidden md:flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded border border-neon-on/30 bg-neon-on/5">
            <span className="dot bg-neon-on shadow-glow-on animate-pulseGlow" />
            <span className="mono text-[11px] tracking-widest text-neon-on">
              REALTIME
            </span>
          </div>
          <ModeBadge />
          <Clock />
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden sm:block text-right">
            <div className="mono text-[10px] tracking-widest text-ink-muted leading-none">
              OPERADOR
            </div>
            <div className="mono text-[12px] text-ink leading-tight truncate max-w-[200px]" data-testid="user-email">
              {user?.email}
            </div>
          </div>
          <button
            data-testid="logout-btn"
            onClick={() => signOut()}
            className="flex items-center gap-2 px-3 py-1.5 rounded border border-line/60 hover:border-neon-crit/60 hover:text-neon-crit text-ink-dim transition mono text-[11px] tracking-widest"
          >
            <LogOut className="w-3.5 h-3.5" />
            SALIR
          </button>
        </div>
      </header>

      <div className="flex flex-1 min-h-0 relative z-10">
        <nav className="hidden md:flex w-56 flex-col border-r border-line/40 bg-bg-900/60 backdrop-blur px-3 py-6">
          <div className="mono text-[10px] tracking-[0.28em] text-ink-muted px-2 mb-3">
            NAVEGACIÓN
          </div>
          {NAV.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                data-testid={item.testid}
                className={({ isActive }) =>
                  [
                    'group relative flex items-center gap-3 px-3 py-2.5 my-0.5 rounded transition mono text-[12px] tracking-wider',
                    isActive
                      ? 'bg-neon-cyan/10 text-neon-cyan border border-neon-cyan/30'
                      : 'text-ink-dim hover:text-ink hover:bg-line/20 border border-transparent',
                  ].join(' ')
                }
              >
                <Icon className="w-4 h-4" strokeWidth={1.6} />
                <span className="uppercase">{item.label}</span>
              </NavLink>
            );
          })}

          <div className="mt-auto pt-6 border-t border-line/40">
            <div className="mono text-[10px] tracking-widest text-ink-muted flex items-center gap-2">
              <Radio className="w-3 h-3 animate-blink text-neon-on" />
              STREAM ACTIVO
            </div>
          </div>
        </nav>

        <nav className="md:hidden fixed bottom-0 left-0 right-0 z-20 border-t border-line/40 bg-bg-900/95 backdrop-blur flex">
          {NAV.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                data-testid={item.testid + '-mobile'}
                className={({ isActive }) =>
                  [
                    'flex-1 flex flex-col items-center justify-center py-2.5 mono text-[10px] tracking-widest',
                    isActive ? 'text-neon-cyan' : 'text-ink-dim',
                  ].join(' ')
                }
              >
                <Icon className="w-5 h-5 mb-0.5" strokeWidth={1.5} />
                {item.label.toUpperCase()}
              </NavLink>
            );
          })}
        </nav>

        <main className="flex-1 min-w-0 p-4 md:p-6 pb-20 md:pb-6 overflow-x-hidden">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
