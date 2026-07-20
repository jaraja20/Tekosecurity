import React, { useEffect, useState, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldAlert,
  Radio,
  Zap,
  Cpu,
  RefreshCw,
  ChevronRight,
  Skull,
} from 'lucide-react';
import { toast } from 'sonner';
import { supabase } from '../lib/supabase';
import { isSameDay } from '../lib/format';
import MetricCard from '../components/MetricCard';
import AlertRow from '../components/AlertRow';

async function fetchLatestNvrStatus() {
  const { data, error } = await supabase
    .from('hikvision_events')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(200);
  if (error) throw error;
  const latest = new Map();
  for (const row of data || []) {
    if (!latest.has(row.nvr_id)) latest.set(row.nvr_id, row);
  }
  return Array.from(latest.values()).sort((a, b) => a.nvr_id - b.nvr_id);
}

async function fetchActiveAlerts() {
  const { data, error } = await supabase
    .from('attacks')
    .select('*')
    .eq('status', 'ACTIVE')
    .order('created_at', { ascending: false })
    .limit(50);
  if (error) throw error;
  return data || [];
}

async function fetchAllAttacksToday() {
  const start = new Date();
  start.setHours(0, 0, 0, 0);
  const { data, error } = await supabase
    .from('attacks')
    .select('id, created_at, severity')
    .gte('created_at', start.toISOString())
    .limit(500);
  if (error) throw error;
  return data || [];
}

export default function DashboardHome() {
  const [activeAlerts, setActiveAlerts] = useState([]);
  const [nvrs, setNvrs] = useState([]);
  const [today, setToday] = useState([]);
  const [loading, setLoading] = useState(true);
  const [closing, setClosing] = useState(null);
  const audioRef = useRef(null);

  const loadAll = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const [alerts, nvrList, todayList] = await Promise.all([
        fetchActiveAlerts(),
        fetchLatestNvrStatus(),
        fetchAllAttacksToday(),
      ]);
      setActiveAlerts(alerts);
      setNvrs(nvrList);
      setToday(todayList);
    } catch (e) {
      toast.error('Error cargando datos: ' + e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAll();
    // realtime: new attacks
    const attackChannel = supabase
      .channel('rt-attacks-home')
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'attacks' },
        (payload) => {
          const newAlert = payload.new;
          if (newAlert.status === 'ACTIVE') {
            setActiveAlerts((prev) => [newAlert, ...prev].slice(0, 50));
            setToday((prev) => [newAlert, ...prev]);
            toast.warning(
              `Nueva alerta ${newAlert.severity}: ${newAlert.attack_type}`,
              { description: newAlert.source_ip }
            );
            if (audioRef.current) {
              audioRef.current.currentTime = 0;
              audioRef.current.play().catch(() => {});
            }
          }
        }
      )
      .on(
        'postgres_changes',
        { event: 'UPDATE', schema: 'public', table: 'attacks' },
        (payload) => {
          const upd = payload.new;
          setActiveAlerts((prev) =>
            upd.status === 'ACTIVE'
              ? prev.map((a) => (a.id === upd.id ? upd : a))
              : prev.filter((a) => a.id !== upd.id)
          );
        }
      )
      .subscribe();

    const nvrChannel = supabase
      .channel('rt-nvr-home')
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'hikvision_events' },
        () => {
          fetchLatestNvrStatus().then(setNvrs).catch(() => {});
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(attackChannel);
      supabase.removeChannel(nvrChannel);
    };
  }, [loadAll]);

  async function handleClose(alert) {
    setClosing(alert.id);
    const { error } = await supabase
      .from('attacks')
      .update({ status: 'CLOSED' })
      .eq('id', alert.id);
    setClosing(null);
    if (error) {
      toast.error('Error cerrando alerta: ' + error.message);
      return;
    }
    setActiveAlerts((prev) => prev.filter((a) => a.id !== alert.id));
    toast.success(`Alerta #${alert.id} resuelta`);
  }

  const onlineCount = nvrs.filter(
    (n) => (n.status || '').toUpperCase() === 'ONLINE'
  ).length;
  const totalNvrs = nvrs.length;

  const criticalCount = activeAlerts.filter(
    (a) => (a.severity || '').toUpperCase() === 'CRITICAL'
  ).length;

  const todayCount = today.filter((a) => isSameDay(a.created_at, new Date())).length;

  return (
    <div className="space-y-6" data-testid="dashboard-home">
      {/* audio ping for new alerts */}
      <audio
        ref={audioRef}
        src="data:audio/wav;base64,UklGRl9vT19XQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQBvT18AAAA="
      />

      {/* Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          testid="metric-active-alerts"
          label="ALERTAS ACTIVAS"
          value={activeAlerts.length}
          sub={
            criticalCount > 0
              ? `${criticalCount} críticas en curso`
              : 'sin alertas críticas'
          }
          accent={activeAlerts.length > 0 ? '#ff1744' : '#4ade80'}
          icon={ShieldAlert}
        />
        <MetricCard
          testid="metric-nvrs"
          label="NVRs ONLINE"
          value={`${onlineCount}/${totalNvrs || 0}`}
          sub={
            totalNvrs === 0
              ? 'sin datos'
              : `${Math.round((onlineCount / Math.max(totalNvrs, 1)) * 100)}% disponibilidad`
          }
          accent={
            totalNvrs === 0
              ? '#8a94a6'
              : onlineCount === totalNvrs
              ? '#00ff88'
              : '#ff9100'
          }
          icon={Cpu}
          trend={
            totalNvrs > 0
              ? {
                  pct: (onlineCount / totalNvrs) * 100,
                  label: `${onlineCount}/${totalNvrs}`,
                }
              : null
          }
        />
        <MetricCard
          testid="metric-today"
          label="ATAQUES HOY"
          value={todayCount}
          sub={new Date().toLocaleDateString('es-PY', { dateStyle: 'long' })}
          accent="#00bfff"
          icon={Zap}
        />
        <MetricCard
          testid="metric-stream"
          label="STREAM STATUS"
          value="LIVE"
          sub="Supabase Realtime activo"
          accent="#00ff88"
          icon={Radio}
        />
      </div>

      {/* Live alerts + NVR overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="panel lg:col-span-2 flex flex-col min-h-[420px]">
          <div className="panel-heading">
            <div className="flex items-center gap-2">
              <Skull className="w-3.5 h-3.5 text-neon-crit" />
              Alertas en Tiempo Real
              {activeAlerts.length > 0 && (
                <span className="ml-2 px-1.5 rounded bg-neon-crit/20 text-neon-crit text-[10px]">
                  {activeAlerts.length}
                </span>
              )}
            </div>
            <div className="flex items-center gap-3">
              <button
                data-testid="refresh-btn"
                onClick={() => loadAll()}
                className="flex items-center gap-1.5 text-ink-dim hover:text-neon-cyan transition"
                title="Recargar"
              >
                <RefreshCw
                  className={['w-3.5 h-3.5', loading ? 'animate-spin' : ''].join(
                    ' '
                  )}
                />
                <span className="mono text-[10px] tracking-widest">REFRESH</span>
              </button>
              <Link
                to="/alerts"
                className="flex items-center gap-1 text-ink-dim hover:text-neon-cyan transition mono text-[10px] tracking-widest"
              >
                VER TODAS <ChevronRight className="w-3 h-3" />
              </Link>
            </div>
          </div>

          <div className="divide-y divide-line/30 overflow-y-auto max-h-[520px]">
            {loading && (
              <div className="p-8 text-center text-ink-dim mono text-xs animate-pulse">
                Cargando alertas...
              </div>
            )}
            {!loading && activeAlerts.length === 0 && (
              <div className="p-10 text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full border border-neon-on/40 bg-neon-on/10 mb-3 shadow-glow-on">
                  <ShieldAlert className="w-6 h-6 text-neon-on" />
                </div>
                <div className="mono text-[12px] tracking-widest text-neon-on">
                  ESTADO SEGURO
                </div>
                <div className="mt-1 text-ink-dim text-[13px]">
                  No hay alertas activas. Todo el perímetro está limpio.
                </div>
              </div>
            )}
            {activeAlerts.map((alert) => (
              <AlertRow
                key={alert.id}
                alert={alert}
                onClose={handleClose}
                closing={closing === alert.id}
              />
            ))}
          </div>
        </section>

        <section className="panel flex flex-col">
          <div className="panel-heading">
            <span>NVRs Hikvision</span>
            <Link
              to="/nvrs"
              className="text-ink-dim hover:text-neon-cyan flex items-center gap-1 mono text-[10px] tracking-widest"
            >
              DETALLES <ChevronRight className="w-3 h-3" />
            </Link>
          </div>
          <ul className="divide-y divide-line/30">
            {nvrs.length === 0 && !loading && (
              <li className="p-6 text-center text-ink-dim text-[13px]">
                Sin datos de NVRs aún.
              </li>
            )}
            {nvrs.map((n) => {
              const isOnline = (n.status || '').toUpperCase() === 'ONLINE';
              const accent = isOnline ? '#00ff88' : '#ff0040';
              return (
                <li
                  key={n.nvr_id}
                  data-testid={`nvr-mini-${n.nvr_id}`}
                  className="flex items-center gap-3 px-4 py-2.5 hover:bg-line/10 transition"
                >
                  <span
                    className="dot"
                    style={{
                      background: accent,
                      boxShadow: `0 0 6px ${accent}`,
                    }}
                  />
                  <div className="min-w-0 flex-1">
                    <div className="text-[13px] text-ink truncate">
                      {n.nvr_name}
                    </div>
                    <div className="mono text-[10px] text-ink-muted truncate">
                      {n.nvr_ip}
                    </div>
                  </div>
                  <span
                    className="mono text-[10px] tracking-widest font-semibold"
                    style={{ color: accent }}
                  >
                    {isOnline ? 'ON' : 'OFF'}
                  </span>
                </li>
              );
            })}
          </ul>
        </section>
      </div>
    </div>
  );
}
