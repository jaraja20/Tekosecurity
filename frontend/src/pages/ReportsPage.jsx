import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { toast } from 'sonner';
import {
  FileSpreadsheet,
  Download,
  RefreshCw,
  AlertTriangle,
  Calendar,
  TrendingUp,
  ShieldAlert,
  Target,
} from 'lucide-react';
import { apiFetch, ApiError } from '../lib/api';
import { supabase } from '../lib/supabase';
import { SEVERITY_META, severityStyle } from '../lib/format';

const BACKEND = (process.env.REACT_APP_BACKEND_URL || '').replace(/\/$/, '');

const PRESETS = [
  { key: '24h', label: 'Últimas 24h', days: 1 },
  { key: '7d', label: 'Últimos 7 días', days: 7 },
  { key: '30d', label: 'Últimos 30 días', days: 30 },
  { key: '90d', label: 'Últimos 90 días', days: 90 },
];

const TYPE_ACCENT = {
  BRUTE_FORCE: '#ff1744',
  DDoS: '#ff9100',
  PORT_SCAN: '#00bfff',
  ANOMALOUS_TRAFFIC: '#ffeb3b',
  NVR_OFFLINE: '#ff0040',
};

function Bar({ value, max, color = '#00bfff', height = 6 }) {
  const pct = max > 0 ? Math.max(3, Math.round((value / max) * 100)) : 0;
  return (
    <div className="w-full bg-line/25 rounded" style={{ height }}>
      <div
        className="rounded transition-all"
        style={{
          width: `${pct}%`,
          height: '100%',
          background: color,
          boxShadow: `0 0 6px ${color}80`,
        }}
      />
    </div>
  );
}

function KpiBox({ label, value, accent = '#00bfff', icon: Icon }) {
  return (
    <div
      className="panel p-4 relative overflow-hidden"
      style={{ boxShadow: `inset 0 0 0 1px ${accent}15` }}
    >
      <div
        className="absolute top-0 left-0 h-full w-[2px]"
        style={{ background: accent, boxShadow: `0 0 8px ${accent}` }}
      />
      <div className="flex items-start justify-between">
        <div>
          <div className="mono text-[10px] tracking-widest text-ink-muted">
            {label}
          </div>
          <div
            className="mt-1 font-semibold mono tabular-nums"
            style={{
              fontSize: 26,
              lineHeight: 1,
              color: accent,
              textShadow: `0 0 12px ${accent}55`,
            }}
          >
            {value}
          </div>
        </div>
        {Icon && (
          <Icon className="w-4 h-4 opacity-70" style={{ color: accent }} />
        )}
      </div>
    </div>
  );
}

export default function ReportsPage() {
  const [preset, setPreset] = useState('30d');
  const [customFrom, setCustomFrom] = useState('');
  const [customTo, setCustomTo] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [downloading, setDownloading] = useState(false);

  const currentRange = useMemo(() => {
    if (customFrom || customTo) {
      return {
        from: customFrom ? new Date(customFrom).toISOString() : null,
        to: customTo ? new Date(customTo + 'T23:59:59').toISOString() : null,
        days: null,
        isCustom: true,
      };
    }
    const p = PRESETS.find((x) => x.key === preset) || PRESETS[2];
    return { from: null, to: null, days: p.days, isCustom: false };
  }, [preset, customFrom, customTo]);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const q = new URLSearchParams();
      if (currentRange.isCustom) {
        if (currentRange.from) q.set('date_from', currentRange.from);
        if (currentRange.to) q.set('date_to', currentRange.to);
      } else {
        q.set('days', String(currentRange.days));
      }
      const json = await apiFetch(`/api/reports/summary?${q.toString()}`);
      setData(json);
    } catch (e) {
      const msg =
        e instanceof ApiError && e.status === 401
          ? 'Sesión expirada. Recarga la página.'
          : e.message || 'Error cargando reportes';
      setError({ status: e.status, message: msg });
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  }, [currentRange]);

  useEffect(() => {
    load();
  }, [load]);

  async function downloadXlsx() {
    setDownloading(true);
    try {
      const { data: sessionData } = await supabase.auth.getSession();
      let token = sessionData?.session?.access_token;
      if (!token) {
        const r = await supabase.auth.refreshSession();
        token = r.data?.session?.access_token;
      }
      if (!token) {
        toast.error('Sesión expirada.');
        return;
      }
      const q = new URLSearchParams();
      if (currentRange.isCustom) {
        if (currentRange.from) q.set('date_from', currentRange.from);
        if (currentRange.to) q.set('date_to', currentRange.to);
      } else {
        q.set('days', String(currentRange.days));
      }
      q.set('token_qs', token);
      // trigger native download by opening in same tab (browser will save)
      const url = `${BACKEND}/api/reports/export.xlsx?${q.toString()}`;
      window.location.href = url;
      toast.success('Descargando Excel…');
    } catch (e) {
      toast.error(e.message || 'Error descargando');
    } finally {
      setTimeout(() => setDownloading(false), 1500);
    }
  }

  const summary = data?.summary;
  const total = summary?.total || 0;
  const maxTypeCount = summary?.by_type?.[0]?.count || 1;
  const maxIpCount = summary?.top_source_ips?.[0]?.count || 1;
  const maxDayCount = Math.max(...(summary?.per_day || []).map((p) => p.count), 1);

  return (
    <div className="space-y-5" data-testid="reports-page">
      {/* Header + filters */}
      <div className="panel p-4">
        <div className="flex flex-col lg:flex-row lg:items-center gap-3">
          <div className="flex items-center gap-3">
            <FileSpreadsheet className="w-5 h-5 text-neon-cyan" strokeWidth={1.6} />
            <div>
              <div className="mono text-[10px] tracking-widest text-ink-muted">
                REPORTES · ANÁLISIS DE AMENAZAS
              </div>
              <div className="text-[15px] font-semibold">
                {total} amenaza{total !== 1 ? 's' : ''} en el periodo
              </div>
            </div>
          </div>

          <div className="flex-1" />

          {/* Presets */}
          <div className="flex flex-wrap items-center gap-1.5">
            {PRESETS.map((p) => (
              <button
                key={p.key}
                data-testid={`reports-preset-${p.key}`}
                onClick={() => {
                  setPreset(p.key);
                  setCustomFrom('');
                  setCustomTo('');
                }}
                className={[
                  'px-2.5 py-1 rounded border mono text-[10px] tracking-widest transition',
                  preset === p.key && !customFrom && !customTo
                    ? 'bg-neon-cyan/15 border-neon-cyan/60 text-neon-cyan'
                    : 'border-line/50 text-ink-dim hover:text-ink',
                ].join(' ')}
              >
                {p.label.toUpperCase()}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-ink-muted" />
            <input
              data-testid="reports-date-from"
              type="date"
              value={customFrom}
              onChange={(e) => setCustomFrom(e.target.value)}
              className="bg-bg-950/70 border border-line/50 rounded px-2 py-1 mono text-[11px] text-ink"
            />
            <span className="text-ink-muted">→</span>
            <input
              data-testid="reports-date-to"
              type="date"
              value={customTo}
              onChange={(e) => setCustomTo(e.target.value)}
              className="bg-bg-950/70 border border-line/50 rounded px-2 py-1 mono text-[11px] text-ink"
            />
          </div>

          <button
            data-testid="reports-refresh"
            onClick={load}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded border border-line/50 text-ink-dim hover:text-neon-cyan hover:border-neon-cyan/50 transition mono text-[10px] tracking-widest"
          >
            <RefreshCw className={loading ? 'w-3 h-3 animate-spin' : 'w-3 h-3'} />
            RELOAD
          </button>

          <button
            data-testid="reports-download"
            onClick={downloadXlsx}
            disabled={downloading || loading || total === 0}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded border border-neon-on/50 bg-neon-on/10 text-neon-on hover:bg-neon-on/20 transition mono text-[11px] tracking-widest shadow-glow-on disabled:opacity-50"
          >
            <Download className={downloading ? 'w-3 h-3 animate-pulse' : 'w-3 h-3'} />
            {downloading ? 'DESCARGANDO…' : 'DESCARGAR EXCEL'}
          </button>
        </div>

        {data?.range && (
          <div className="mt-3 pt-3 border-t border-line/30 mono text-[10px] tracking-widest text-ink-muted">
            RANGO EN VIGOR: {data.range.from || '(inicio)'} → {data.range.to || '(hoy)'}
          </div>
        )}
      </div>

      {/* Error state */}
      {!loading && error && (
        <div
          data-testid="reports-error"
          className="panel p-6 border-neon-crit/40 flex items-start gap-3"
        >
          <AlertTriangle className="w-5 h-5 text-neon-crit flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <div className="mono text-[12px] tracking-widest text-neon-crit">
              ERROR AL CARGAR REPORTES
              {error.status ? ` — HTTP ${error.status}` : ''}
            </div>
            <div className="text-[13px] mt-1 text-ink-dim">{error.message}</div>
            <button
              onClick={load}
              className="mt-3 px-3 py-1.5 rounded border border-neon-cyan/50 bg-neon-cyan/10 text-neon-cyan mono text-[11px] tracking-widest hover:bg-neon-cyan/20"
            >
              REINTENTAR
            </button>
          </div>
        </div>
      )}

      {loading && !summary && (
        <div className="panel p-8 text-center text-ink-dim mono text-xs animate-pulse">
          Calculando estadísticas…
        </div>
      )}

      {summary && total === 0 && !error && (
        <div className="panel p-10 text-center">
          <TrendingUp className="w-8 h-8 text-ink-muted mx-auto mb-2" />
          <div className="mono text-[12px] tracking-widest text-ink-dim">
            SIN AMENAZAS EN EL PERIODO SELECCIONADO
          </div>
        </div>
      )}

      {summary && total > 0 && (
        <>
          {/* KPI row */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            <KpiBox
              label="TOTAL"
              value={total}
              accent="#00bfff"
              icon={ShieldAlert}
            />
            {summary.by_severity.map((s) => (
              <KpiBox
                key={s.severity}
                label={s.severity}
                value={s.count}
                accent={SEVERITY_META[s.severity]?.color || '#8a94a6'}
              />
            ))}
          </div>

          {/* Types + Top IPs */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <section className="panel">
              <div className="panel-heading">
                <span>Amenazas por Tipo</span>
                <span className="text-ink-muted normal-case tracking-normal">
                  {summary.by_type.length} categorías
                </span>
              </div>
              <div className="p-4 space-y-3" data-testid="reports-by-type">
                {summary.by_type.map((row) => {
                  const color = TYPE_ACCENT[row.attack_type] || '#00bfff';
                  const pct = Math.round((row.count / total) * 100);
                  return (
                    <div
                      key={row.attack_type}
                      data-testid={`type-row-${row.attack_type}`}
                    >
                      <div className="flex items-baseline justify-between mono text-[12px] mb-1">
                        <span className="text-ink font-semibold tracking-wide">
                          {row.attack_type}
                        </span>
                        <span className="text-ink-dim">
                          <span
                            className="font-semibold tabular-nums"
                            style={{ color }}
                            data-testid={`type-count-${row.attack_type}`}
                          >
                            {row.count}
                          </span>
                          <span className="text-ink-muted ml-2">
                            {pct}%
                          </span>
                        </span>
                      </div>
                      <Bar value={row.count} max={maxTypeCount} color={color} />
                    </div>
                  );
                })}
              </div>
            </section>

            <section className="panel">
              <div className="panel-heading">
                <span>Top IPs Atacantes</span>
                <Target className="w-3.5 h-3.5 text-ink-muted" />
              </div>
              <div className="p-4 space-y-2" data-testid="reports-top-ips">
                {summary.top_source_ips.length === 0 && (
                  <div className="text-center text-ink-muted text-[13px] py-6">
                    Sin IPs registradas.
                  </div>
                )}
                {summary.top_source_ips.map((row, i) => (
                  <div
                    key={row.source_ip}
                    className="flex items-center gap-3"
                    data-testid={`ip-row-${row.source_ip}`}
                  >
                    <span className="mono text-[10px] text-ink-muted w-6">
                      #{i + 1}
                    </span>
                    <span className="mono text-[12px] text-neon-cyan flex-shrink-0 w-32 truncate">
                      {row.source_ip}
                    </span>
                    <div className="flex-1">
                      <Bar
                        value={row.count}
                        max={maxIpCount}
                        color="#ff9100"
                        height={5}
                      />
                    </div>
                    <span className="mono text-[11px] text-ink tabular-nums w-10 text-right">
                      {row.count}
                    </span>
                  </div>
                ))}
              </div>
            </section>
          </div>

          {/* Cross table types × severity */}
          <section className="panel">
            <div className="panel-heading">
              <span>Matriz Tipo × Severidad</span>
              <span className="text-ink-muted normal-case tracking-normal">
                {Object.keys(summary.type_by_severity).length} tipos
              </span>
            </div>
            <div className="overflow-x-auto">
              <table
                className="w-full mono text-[12px]"
                data-testid="reports-matrix"
              >
                <thead>
                  <tr className="border-b border-line/40">
                    <th className="text-left p-3 text-[10px] tracking-widest text-ink-muted">
                      TIPO
                    </th>
                    {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => (
                      <th
                        key={sev}
                        className="text-right p-3 text-[10px] tracking-widest"
                        style={{
                          color: SEVERITY_META[sev]?.color || '#8a94a6',
                        }}
                      >
                        {sev}
                      </th>
                    ))}
                    <th className="text-right p-3 text-[10px] tracking-widest text-ink">
                      TOTAL
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(summary.type_by_severity).map(([type, sevs]) => {
                    const rowTotal = Object.values(sevs).reduce(
                      (a, b) => a + b,
                      0
                    );
                    return (
                      <tr
                        key={type}
                        className="border-b border-line/20 hover:bg-line/10"
                      >
                        <td className="p-3 text-ink font-semibold">{type}</td>
                        {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => {
                          const v = sevs[sev] || 0;
                          const style = v > 0 ? severityStyle(sev) : {};
                          return (
                            <td key={sev} className="p-3 text-right">
                              {v > 0 ? (
                                <span
                                  className="chip inline-block"
                                  style={{ ...style, minWidth: 32, textAlign: 'center' }}
                                >
                                  {v}
                                </span>
                              ) : (
                                <span className="text-ink-muted">·</span>
                              )}
                            </td>
                          );
                        })}
                        <td className="p-3 text-right text-ink font-semibold tabular-nums">
                          {rowTotal}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>

          {/* Time series */}
          {summary.per_day.length > 0 && (
            <section className="panel">
              <div className="panel-heading">
                <span>Serie temporal (por día)</span>
                <span className="text-ink-muted normal-case tracking-normal">
                  {summary.per_day.length} días con actividad
                </span>
              </div>
              <div
                className="p-4 flex items-end gap-1 h-40 overflow-x-auto"
                data-testid="reports-timeline"
              >
                {summary.per_day.map((d) => {
                  const pct = Math.max(4, (d.count / maxDayCount) * 100);
                  return (
                    <div
                      key={d.date}
                      className="flex flex-col items-center gap-1 min-w-[28px]"
                      title={`${d.date}: ${d.count} amenazas`}
                    >
                      <div className="mono text-[9px] text-ink-dim tabular-nums">
                        {d.count}
                      </div>
                      <div
                        className="w-4 rounded-t transition-all"
                        style={{
                          height: `${pct}%`,
                          background:
                            d.count > maxDayCount * 0.66
                              ? '#ff1744'
                              : d.count > maxDayCount * 0.33
                              ? '#ff9100'
                              : '#00bfff',
                          boxShadow: '0 0 8px currentColor',
                        }}
                      />
                      <div className="mono text-[8px] text-ink-muted tracking-widest">
                        {d.date.slice(5)}
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>
          )}

          <div className="text-center mono text-[10px] tracking-widest text-ink-muted pt-2">
            El Excel incluye 5 hojas: Resumen · Tipos por Severidad · Top IPs · Serie temporal · Detalle completo
          </div>
        </>
      )}
    </div>
  );
}
