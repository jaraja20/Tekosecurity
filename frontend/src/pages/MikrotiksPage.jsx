import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Router,
  MapPin,
  RefreshCw,
  ShieldCheck,
  Zap,
  Wifi,
  Network,
  AlertTriangle,
} from 'lucide-react';
import { apiFetch, ApiError } from '../lib/api';

const PRIORITY_STYLE = {
  CRITICAL: { color: '#ff1744', bg: 'rgba(255,23,68,0.10)' },
  HIGH: { color: '#ff9100', bg: 'rgba(255,145,0,0.10)' },
  MEDIUM: { color: '#ffeb3b', bg: 'rgba(255,235,59,0.10)' },
  LOW: { color: '#4ade80', bg: 'rgba(74,222,128,0.10)' },
};

const ROLE_ICON = {
  VPN_SERVER_HUB: ShieldCheck,
  VPN_CLIENT: Wifi,
};

function MikrotikCard({ mk, blockCount }) {
  const prio = PRIORITY_STYLE[mk.priority] || PRIORITY_STYLE.MEDIUM;
  const RoleIcon = ROLE_ICON[mk.role] || Network;
  const isHub = mk.role === 'VPN_SERVER_HUB';

  return (
    <div
      data-testid={`mikrotik-card-${mk.name}`}
      className="panel p-4 relative overflow-hidden transition hover:border-neon-cyan/40"
      style={{ boxShadow: `inset 0 0 0 1px ${prio.color}22` }}
    >
      <div
        className="absolute inset-x-0 top-0 h-[2px]"
        style={{ background: prio.color, boxShadow: `0 0 12px ${prio.color}` }}
      />

      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <Router className="w-4 h-4 text-neon-cyan" strokeWidth={1.6} />
            <h3
              className="text-[14px] font-semibold tracking-tight truncate"
              data-testid={`mikrotik-name-${mk.name}`}
            >
              {mk.name}
            </h3>
            {isHub && (
              <span
                className="chip"
                style={{
                  color: '#00bfff',
                  background: 'rgba(0,191,255,0.10)',
                  borderColor: 'rgba(0,191,255,0.4)',
                }}
                title="Servidor VPN principal (HUB)"
              >
                <Zap className="w-3 h-3" />
                HUB
              </span>
            )}
          </div>
          <div className="mt-0.5 flex items-center gap-1.5 mono text-[10px] text-ink-muted">
            <MapPin className="w-3 h-3" />
            <span className="truncate">{mk.location}</span>
          </div>
        </div>

        <div
          className="flex-shrink-0 flex items-center gap-1.5 px-2 py-1 rounded mono text-[10px] tracking-widest font-semibold"
          style={{
            color: prio.color,
            background: prio.bg,
            border: `1px solid ${prio.color}55`,
          }}
          data-testid={`mikrotik-priority-${mk.name}`}
        >
          {mk.priority}
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 text-[11px]">
        <div>
          <div className="mono text-[9px] tracking-widest text-ink-muted">
            IP LAN
          </div>
          <div className="mono text-ink" data-testid={`mikrotik-ip-${mk.name}`}>
            {mk.ip}
          </div>
        </div>
        <div>
          <div className="mono text-[9px] tracking-widest text-ink-muted">
            ROL
          </div>
          <div className="mono text-ink flex items-center gap-1.5">
            <RoleIcon className="w-3 h-3 text-ink-dim" />
            {mk.role?.replace(/_/g, ' ')}
          </div>
        </div>
        {mk.management_ip && (
          <div>
            <div className="mono text-[9px] tracking-widest text-ink-muted">
              IP PÚBLICA
            </div>
            <div className="mono text-ink truncate">{mk.management_ip}</div>
          </div>
        )}
        <div>
          <div className="mono text-[9px] tracking-widest text-ink-muted">
            SUBNET
          </div>
          <div className="mono text-ink-dim truncate">{mk.lan_subnet}</div>
        </div>
        <div className="col-span-2">
          <div className="mono text-[9px] tracking-widest text-ink-muted">
            MODELO
          </div>
          <div className="mono text-[11px] text-ink-dim truncate">{mk.model}</div>
        </div>
        {mk.description && (
          <div className="col-span-2">
            <div className="mono text-[9px] tracking-widest text-ink-muted">
              DESCRIPCIÓN
            </div>
            <div className="text-[11px] text-ink-dim leading-relaxed">
              {mk.description}
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 pt-3 border-t border-line/40 flex items-center justify-between gap-2 text-[10px]">
        <div className="flex items-center gap-3 mono tracking-widest text-ink-muted">
          {mk.firewall_enabled && (
            <span className="flex items-center gap-1 text-neon-on">
              <ShieldCheck className="w-3 h-3" /> FW
            </span>
          )}
          {mk.vpn_server && (
            <span className="flex items-center gap-1 text-neon-cyan">
              VPN·SRV
            </span>
          )}
          {mk.vpn_client && (
            <span className="flex items-center gap-1 text-ink-dim">
              VPN·CLI
            </span>
          )}
          {mk.ospf_enabled && (
            <span className="flex items-center gap-1 text-ink-dim">OSPF</span>
          )}
        </div>
        <div
          className="mono text-[10px] tracking-widest"
          data-testid={`mikrotik-blocks-${mk.name}`}
          title="Bloqueos en las últimas 24h que incluyeron esta sucursal"
          style={{ color: (blockCount || 0) > 0 ? '#ff9100' : '#5a6478' }}
        >
          {blockCount || 0} BLOQ 24H
        </div>
      </div>
    </div>
  );
}

export default function MikrotiksPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [blocksByHost, setBlocksByHost] = useState({});
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [mkJson, auditJson] = await Promise.all([
        apiFetch('/api/mikrotiks'),
        apiFetch('/api/actions/audit-log?limit=200').catch(() => ({ entries: [] })),
      ]);
      setData(mkJson);

      const counts = {};
      const cutoff = Date.now() - 24 * 3600 * 1000;
      for (const entry of auditJson.entries || []) {
        if (entry.action !== 'BLOCK_IP_REAL') continue;
        if (entry.status === 'FAILED') continue;
        if (new Date(entry.created_at).getTime() < cutoff) continue;
        try {
          const det =
            typeof entry.details === 'string'
              ? JSON.parse(entry.details)
              : entry.details || {};
          for (const host of det.successful || []) {
            counts[host] = (counts[host] || 0) + 1;
          }
        } catch (_) {
          /* ignore malformed */
        }
      }
      setBlocksByHost(counts);
    } catch (e) {
      const msg =
        e instanceof ApiError && e.status === 401
          ? 'Sesión expirada. Recarga la página.'
          : e.message || 'Error cargando Mikrotiks';
      setError({ status: e.status, message: msg });
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const list = data?.mikrotiks || [];
  const mode = data?.mode;

  return (
    <div className="space-y-5" data-testid="mikrotiks-page">
      <div className="panel p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Router className="w-5 h-5 text-neon-cyan" strokeWidth={1.6} />
          <div>
            <div className="mono text-[10px] tracking-widest text-ink-muted">
              GATEWAYS MIKROTIK — INFRAESTRUCTURA DE RED
            </div>
            <div className="text-[15px] font-semibold">
              {list.length} dispositivo{list.length !== 1 ? 's' : ''} configurado
              {list.length !== 1 ? 's' : ''}
              {mode && (
                <span
                  className="ml-3 mono text-[11px] tracking-widest"
                  style={{
                    color:
                      mode === 'REAL_ACTIONS' ? '#00ff88' : '#ff9100',
                  }}
                >
                  MODE: {mode}
                </span>
              )}
            </div>
          </div>
        </div>
        <button
          data-testid="mikrotiks-refresh"
          onClick={load}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded border border-line/50 text-ink-dim hover:text-neon-cyan hover:border-neon-cyan/50 transition mono text-[10px] tracking-widest"
        >
          <RefreshCw className={loading ? 'w-3 h-3 animate-spin' : 'w-3 h-3'} />
          RELOAD
        </button>
      </div>

      {loading && list.length === 0 && (
        <div className="panel p-8 text-center text-ink-dim mono text-xs animate-pulse">
          Cargando gateways...
        </div>
      )}

      {!loading && error && (
        <div
          data-testid="mikrotiks-error"
          className="panel p-6 border-neon-crit/40 flex items-start gap-3"
        >
          <AlertTriangle className="w-5 h-5 text-neon-crit flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <div className="mono text-[12px] tracking-widest text-neon-crit">
              ERROR AL CARGAR GATEWAYS
              {error.status ? ` — HTTP ${error.status}` : ''}
            </div>
            <div className="text-[13px] mt-1 text-ink-dim">
              {error.message}
            </div>
            <div className="mt-3">
              <button
                onClick={load}
                data-testid="mikrotiks-retry"
                className="px-3 py-1.5 rounded border border-neon-cyan/50 bg-neon-cyan/10 text-neon-cyan mono text-[11px] tracking-widest hover:bg-neon-cyan/20 transition"
              >
                <RefreshCw className="w-3 h-3 inline mr-1.5" />
                REINTENTAR
              </button>
            </div>
          </div>
        </div>
      )}

      {!loading && !error && data && list.length === 0 && (
        <div className="panel p-8 text-center text-ink-dim">
          <div className="mono text-[12px] tracking-widest">
            SIN GATEWAYS CONFIGURADOS
          </div>
          <div className="text-[13px] mt-1">
            Revisa <code className="mono text-neon-cyan">config/mikrotik_config.json</code>.
          </div>
        </div>
      )}

      {list.length > 0 && (
        <>
          {data?.security_policy && (
            <div className="panel p-4">
              <div className="mono text-[10px] tracking-widest text-ink-muted mb-3">
                POLÍTICA DE SEGURIDAD ACTIVA
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-[11px]">
                <div>
                  <div className="mono text-[9px] tracking-widest text-ink-muted">
                    UMBRAL SSH
                  </div>
                  <div className="mono text-ink">
                    {data.security_policy.block_ssh_after_attempts} intentos
                  </div>
                </div>
                <div>
                  <div className="mono text-[9px] tracking-widest text-ink-muted">
                    VENTANA DETECCIÓN
                  </div>
                  <div className="mono text-ink">
                    {data.security_policy.block_window_minutes} min
                  </div>
                </div>
                <div>
                  <div className="mono text-[9px] tracking-widest text-ink-muted">
                    BLOQUEO TEMPORAL
                  </div>
                  <div className="mono text-ink">
                    {data.security_policy.temporal_block_hours}h
                  </div>
                </div>
                <div>
                  <div className="mono text-[9px] tracking-widest text-ink-muted">
                    LOGGING
                  </div>
                  <div
                    className="mono"
                    style={{
                      color: data.security_policy.enable_logging
                        ? '#00ff88'
                        : '#5a6478',
                    }}
                  >
                    {data.security_policy.enable_logging ? 'ENABLED' : 'OFF'}
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {list.map((mk) => (
              <Link
                key={mk.name}
                to={`/mikrotiks/${encodeURIComponent(mk.name)}`}
                data-testid={`mikrotik-link-${mk.name}`}
                className="block hover:scale-[1.01] transition-transform"
              >
                <MikrotikCard mk={mk} blockCount={blocksByHost[mk.name] || 0} />
              </Link>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
