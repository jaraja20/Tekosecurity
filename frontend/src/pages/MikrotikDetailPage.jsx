import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { toast } from 'sonner';
import {
  ArrowLeft,
  RefreshCw,
  Cpu,
  Thermometer,
  HardDrive,
  Clock,
  Radio,
  ArrowUpDown,
  ShieldCheck,
  LogIn,
  XCircle,
  AlertTriangle,
} from 'lucide-react';
import { apiFetch, ApiError } from '../lib/api';
import { MetricsStream } from '../lib/metricsStream';

const REFRESH_MS = 1_000; // SSE now sends every 1 second (true real-time)

function fmtBytes(bytes) {
  if (bytes == null) return '—';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let v = bytes;
  let u = 0;
  while (v >= 1024 && u < units.length - 1) {
    v /= 1024;
    u += 1;
  }
  return `${v.toFixed(v < 10 ? 1 : 0)} ${units[u]}`;
}

function timeAgoLocal(iso) {
  if (!iso) return '—';
  const diff = Math.max(0, Math.floor((Date.now() - new Date(iso).getTime()) / 1000));
  if (diff < 60) return `hace ${diff}s`;
  if (diff < 3600) return `hace ${Math.floor(diff / 60)}m`;
  if (diff < 86400) return `hace ${Math.floor(diff / 3600)}h`;
  return `hace ${Math.floor(diff / 86400)}d`;
}

function Gauge({ label, value, unit = '%', warn = 70, crit = 85, icon: Icon }) {
  const v = value == null ? 0 : value;
  const color = v >= crit ? '#ff1744' : v >= warn ? '#ff9100' : '#00ff88';
  const pct = Math.min(100, Math.max(0, v));
  return (
    <div className="panel p-3">
      <div className="flex items-start justify-between">
        <div>
          <div className="mono text-[9px] tracking-widest text-ink-muted">{label}</div>
          <div
            className="mono font-semibold tabular-nums mt-0.5"
            style={{ color, fontSize: 22, lineHeight: 1, textShadow: `0 0 10px ${color}55` }}
          >
            {value == null ? '—' : `${value}${unit}`}
          </div>
        </div>
        {Icon && <Icon className="w-4 h-4 opacity-70" style={{ color }} />}
      </div>
      <div className="mt-2 h-1 bg-line/30 rounded overflow-hidden">
        <div
          className="h-full transition-all"
          style={{ width: `${pct}%`, background: color, boxShadow: `0 0 6px ${color}` }}
        />
      </div>
    </div>
  );
}

export default function MikrotikDetailPage() {
  const { name } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const streamRef = useRef(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      const json = await apiFetch(`/api/mikrotiks/${encodeURIComponent(name)}`);
      setData(json);
    } catch (e) {
      const msg =
        e instanceof ApiError && e.status === 404
          ? `Mikrotik "${name}" no encontrado`
          : e.message || 'Error cargando detalle';
      setError({ status: e.status, message: msg });
      if (!data) toast.error(msg);
    } finally {
      setLoading(false);
    }
  }, [name, data]);

  useEffect(() => {
    setLoading(true);
    load();
  }, [name]); // eslint-disable-line react-hooks/exhaustive-deps

  // Real-time metrics via Server-Sent Events
  useEffect(() => {
    if (!autoRefresh) {
      if (streamRef.current) {
        streamRef.current.disconnect();
        streamRef.current = null;
      }
      return undefined;
    }

    // Get API base URL from current window location
    const apiBase = window.location.origin.includes('vercel.app')
      ? 'https://icy-experts-go.loca.lt'
      : 'http://localhost:8001';

    // Get JWT token from localStorage
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.warn('[MikrotikDetail] No access token found');
      return undefined;
    }

    // Connect to SSE stream
    streamRef.current = new MetricsStream(
      name,
      apiBase,
      token,
      (metrics) => {
        // Update only the metrics part, keep device info
        setData((prev) =>
          prev
            ? {
                ...prev,
                metrics,
              }
            : null
        );
        setLoading(false);
      },
      (error) => {
        console.error('[MikrotikDetail] Stream error:', error);
        setError({
          status: 500,
          message: 'Error en stream de métricas en tiempo real',
        });
      }
    );

    streamRef.current.connect();

    return () => {
      if (streamRef.current) {
        streamRef.current.disconnect();
        streamRef.current = null;
      }
    };
  }, [autoRefresh, name]);

  const dev = data?.device;
  const m = data?.metrics;

  return (
    <div className="space-y-4" data-testid="mikrotik-detail-page">
      {/* Header + back */}
      <div className="flex flex-wrap items-center gap-3">
        <Link
          to="/mikrotiks"
          data-testid="mikrotik-back"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded border border-line/50 text-ink-dim hover:text-neon-cyan hover:border-neon-cyan/50 transition mono text-[11px] tracking-widest"
        >
          <ArrowLeft className="w-3 h-3" />
          MIKROTIKS
        </Link>

        {dev && (
          <div className="flex items-baseline gap-3">
            <h1 className="text-xl font-semibold tracking-tight">{dev.name}</h1>
            <span className="mono text-[11px] text-ink-dim">{dev.location}</span>
            <span className="mono text-[11px] text-neon-cyan">{dev.ip}</span>
          </div>
        )}

        <div className="flex-1" />

        <label
          className="flex items-center gap-1.5 mono text-[10px] tracking-widest text-ink-dim cursor-pointer select-none"
          data-testid="mikrotik-autorefresh"
        >
          <input
            type="checkbox"
            checked={autoRefresh}
            onChange={(e) => setAutoRefresh(e.target.checked)}
            className="accent-neon-cyan"
          />
          AUTO {REFRESH_MS / 1000}s
        </label>

        <button
          data-testid="mikrotik-detail-refresh"
          onClick={load}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded border border-line/50 text-ink-dim hover:text-neon-cyan hover:border-neon-cyan/50 transition mono text-[10px] tracking-widest"
        >
          <RefreshCw className={loading ? 'w-3 h-3 animate-spin' : 'w-3 h-3'} />
          RELOAD
        </button>
      </div>

      {loading && !data && (
        <div className="panel p-8 text-center text-ink-dim mono text-xs animate-pulse">
          Cargando métricas de {name}…
        </div>
      )}

      {error && !data && (
        <div
          data-testid="mikrotik-detail-error"
          className="panel p-6 border-neon-crit/40 flex items-start gap-3"
        >
          <AlertTriangle className="w-5 h-5 text-neon-crit flex-shrink-0 mt-0.5" />
          <div>
            <div className="mono text-[12px] tracking-widest text-neon-crit">
              ERROR {error.status ? `— HTTP ${error.status}` : ''}
            </div>
            <div className="text-[13px] mt-1 text-ink-dim">{error.message}</div>
          </div>
        </div>
      )}

      {m && (
        <>
          {/* System gauges */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3" data-testid="mikrotik-system">
            <Gauge label="CPU LOAD" value={m.system?.cpu_load_pct} icon={Cpu} />
            <Gauge label="MEMORIA" value={m.system?.memory_used_pct} icon={HardDrive} />
            <Gauge
              label="TEMP"
              value={m.system?.temperature_c}
              unit="°C"
              warn={55}
              crit={70}
              icon={Thermometer}
            />
            <Gauge
              label="STORAGE LIBRE"
              value={m.system?.storage_free_pct}
              warn={100}
              crit={100}
              icon={HardDrive}
            />
            <Gauge
              label="UPTIME"
              value={m.system?.uptime_days}
              unit="d"
              warn={100}
              crit={100}
              icon={Clock}
            />
          </div>

          {/* ISPs */}
          <section className="panel">
            <div className="panel-heading">
              <div className="flex items-center gap-2">
                <Radio className="w-3.5 h-3.5 text-neon-cyan" />
                Conectividad · Proveedores
              </div>
              <span className="text-ink-muted normal-case tracking-normal">
                {m.isps.length} ISP{m.isps.length !== 1 ? 's' : ''}
              </span>
            </div>
            <div className="p-4 space-y-3" data-testid="mikrotik-isps">
              {m.isps.map((isp, i) => {
                const lossColor =
                  isp.packet_loss_pct >= 10
                    ? '#ff1744'
                    : isp.packet_loss_pct >= 3
                    ? '#ff9100'
                    : '#00ff88';
                return (
                  <div
                    key={i}
                    data-testid={`isp-row-${i}`}
                    className="border border-line/40 rounded p-3"
                    style={{
                      background: isp.active ? 'rgba(0,255,136,0.04)' : 'transparent',
                      borderColor: isp.active
                        ? 'rgba(0,255,136,0.4)'
                        : 'rgba(30,58,138,0.3)',
                    }}
                  >
                    <div className="flex flex-wrap items-baseline gap-3">
                      <span
                        className="mono text-[10px] tracking-widest font-semibold"
                        style={{
                          color: isp.active ? '#00ff88' : '#8a94a6',
                        }}
                      >
                        {isp.active ? '● ACTIVO' : '○ STANDBY'}
                      </span>
                      <span className="text-[14px] font-semibold text-ink">{isp.name}</span>
                      <span className="mono text-[11px] text-ink-dim">{isp.type}</span>
                      <span className="mono text-[10px] text-ink-muted ml-auto">
                        GW {isp.gateway}
                      </span>
                    </div>

                    <div className="mt-3 grid grid-cols-3 gap-3">
                      <div>
                        <div className="mono text-[9px] tracking-widest text-ink-muted">
                          PACKET LOSS
                        </div>
                        <div
                          className="mono font-semibold tabular-nums"
                          style={{ color: lossColor, fontSize: 18, lineHeight: 1 }}
                        >
                          {isp.packet_loss_pct}%
                        </div>
                        <div className="mt-1.5 h-1 bg-line/30 rounded overflow-hidden">
                          <div
                            className="h-full"
                            style={{
                              width: `${Math.min(100, isp.packet_loss_pct * 5)}%`,
                              background: lossColor,
                              boxShadow: `0 0 4px ${lossColor}`,
                            }}
                          />
                        </div>
                      </div>
                      <div>
                        <div className="mono text-[9px] tracking-widest text-ink-muted">
                          LATENCIA
                        </div>
                        <div
                          className="mono font-semibold tabular-nums text-ink"
                          style={{ fontSize: 18, lineHeight: 1 }}
                        >
                          {isp.latency_ms}
                          <span className="text-[11px] text-ink-muted"> ms</span>
                        </div>
                      </div>
                      <div>
                        <div className="mono text-[9px] tracking-widest text-ink-muted">
                          ESTADO
                        </div>
                        <div
                          className="mono font-semibold"
                          style={{
                            color: isp.status === 'UP' ? '#00ff88' : '#ff9100',
                            fontSize: 14,
                            lineHeight: 1.4,
                          }}
                        >
                          {isp.status}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>

          {/* Failovers + VPNs side by side */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <section className="panel">
              <div className="panel-heading">
                <div className="flex items-center gap-2">
                  <ArrowUpDown className="w-3.5 h-3.5 text-neon-high" />
                  Failovers recientes
                </div>
                <span className="text-ink-muted normal-case tracking-normal">
                  {m.failover_events.length}
                </span>
              </div>
              <ul className="divide-y divide-line/30" data-testid="mikrotik-failovers">
                {m.failover_events.length === 0 && (
                  <li className="p-4 text-center text-ink-dim text-[13px]">
                    Sin cambios de proveedor en las últimas 12h. ✓
                  </li>
                )}
                {m.failover_events.map((e, i) => (
                  <li
                    key={i}
                    className="px-4 py-2.5 flex items-center gap-3"
                    data-testid={`failover-${i}`}
                  >
                    <ArrowUpDown className="w-3.5 h-3.5 text-neon-high flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="mono text-[12px] text-ink truncate">
                        <span className="text-neon-crit">{e.from}</span>
                        <span className="text-ink-muted"> → </span>
                        <span className="text-neon-on">{e.to}</span>
                      </div>
                      <div className="text-[11px] text-ink-dim">{e.reason}</div>
                    </div>
                    <span className="mono text-[10px] text-ink-muted whitespace-nowrap">
                      {timeAgoLocal(e.timestamp)}
                    </span>
                  </li>
                ))}
              </ul>
            </section>

            <section className="panel">
              <div className="panel-heading">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-3.5 h-3.5 text-neon-cyan" />
                  VPNs activas
                </div>
                <span className="text-ink-muted normal-case tracking-normal">
                  {m.vpns.length}
                </span>
              </div>
              <ul className="divide-y divide-line/30" data-testid="mikrotik-vpns">
                {m.vpns.length === 0 && (
                  <li className="p-4 text-center text-ink-dim text-[13px]">
                    Sin túneles activos.
                  </li>
                )}
                {m.vpns.map((v, i) => (
                  <li
                    key={v.name}
                    className="px-4 py-2.5"
                    data-testid={`vpn-${v.name}`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="dot bg-neon-on shadow-glow-on" />
                      <span className="mono text-[12px] text-ink font-semibold">
                        {v.name}
                      </span>
                      <span className="mono text-[10px] text-ink-muted ml-auto">
                        {v.type}
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-[11px] mono">
                      <div>
                        <div className="text-[9px] text-ink-muted tracking-widest">
                          PEER
                        </div>
                        <div className="text-neon-cyan truncate">{v.peer_name}</div>
                      </div>
                      <div>
                        <div className="text-[9px] text-ink-muted tracking-widest">
                          UPTIME
                        </div>
                        <div className="text-ink">{v.uptime_hours}h</div>
                      </div>
                      <div>
                        <div className="text-[9px] text-ink-muted tracking-widest">
                          TX / RX
                        </div>
                        <div className="text-ink">
                          {fmtBytes(v.tx_bytes)} / {fmtBytes(v.rx_bytes)}
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </section>
          </div>

          {/* Login attempts */}
          <section className="panel">
            <div className="panel-heading">
              <div className="flex items-center gap-2">
                <LogIn className="w-3.5 h-3.5 text-neon-high" />
                Intentos de acceso (últimas 12h)
              </div>
              <span className="text-ink-muted normal-case tracking-normal">
                {m.login_attempts.length}
                {' · '}
                <span className="text-neon-crit">
                  {m.login_attempts.filter((l) => !l.success).length} fallidos
                </span>
              </span>
            </div>
            <ul className="divide-y divide-line/30" data-testid="mikrotik-logins">
              {m.login_attempts.map((l, i) => (
                <li
                  key={i}
                  className="px-4 py-2 flex items-center gap-3"
                  data-testid={`login-${i}`}
                >
                  {l.success ? (
                    <ShieldCheck className="w-3.5 h-3.5 text-neon-on flex-shrink-0" />
                  ) : (
                    <XCircle className="w-3.5 h-3.5 text-neon-crit flex-shrink-0" />
                  )}
                  <span
                    className="mono text-[11px] w-16"
                    style={{ color: l.success ? '#00ff88' : '#ff1744' }}
                  >
                    {l.success ? 'OK' : 'FAIL'}
                  </span>
                  <span className="mono text-[11px] text-ink w-16">{l.user}</span>
                  <span className="mono text-[11px] text-neon-cyan flex-1 truncate">
                    {l.source_ip}
                  </span>
                  <span className="mono text-[10px] text-ink-muted w-14">{l.service}</span>
                  <span className="mono text-[10px] text-ink-muted w-16 text-right">
                    {timeAgoLocal(l.timestamp)}
                  </span>
                </li>
              ))}
            </ul>
          </section>

          <div className="mono text-[10px] tracking-widest text-ink-muted text-center">
            Fuente: {m.source} · Actualizado cada 1s en tiempo real
            {m.source === 'DRY_RUN' && ' · métricas simuladas (activá SSH real on-prem para valores reales)'}
          </div>
        </>
      )}
    </div>
  );
}
