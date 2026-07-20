import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { toast } from 'sonner';
import { Filter, RefreshCw, Search } from 'lucide-react';
import { supabase } from '../lib/supabase';
import AlertRow from '../components/AlertRow';
import { SEVERITY_META } from '../lib/format';

const SEVERITIES = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
const STATUSES = ['ACTIVE', 'ALL'];

export default function AlertsPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sevFilter, setSevFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ACTIVE');
  const [q, setQ] = useState('');
  const [closing, setClosing] = useState(null);
  const [sortBy, setSortBy] = useState('recent');

  const load = useCallback(async () => {
    setLoading(true);
    let query = supabase
      .from('attacks')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(300);
    if (statusFilter === 'ACTIVE') query = query.eq('status', 'ACTIVE');
    const { data, error } = await query;
    if (error) {
      toast.error(error.message);
    } else {
      setItems(data || []);
    }
    setLoading(false);
  }, [statusFilter]);

  useEffect(() => {
    load();
    const ch = supabase
      .channel('rt-alerts-page')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'attacks' },
        () => load()
      )
      .subscribe();
    return () => supabase.removeChannel(ch);
  }, [load]);

  const filtered = useMemo(() => {
    let list = items;
    if (sevFilter !== 'ALL')
      list = list.filter(
        (a) => (a.severity || '').toUpperCase() === sevFilter
      );
    if (q.trim()) {
      const s = q.toLowerCase();
      list = list.filter(
        (a) =>
          (a.source_ip || '').toLowerCase().includes(s) ||
          (a.attack_type || '').toLowerCase().includes(s) ||
          (a.details || '').toLowerCase().includes(s)
      );
    }
    if (sortBy === 'severity') {
      list = [...list].sort(
        (a, b) =>
          (SEVERITY_META[b.severity]?.weight || 0) -
          (SEVERITY_META[a.severity]?.weight || 0)
      );
    }
    return list;
  }, [items, sevFilter, q, sortBy]);

  async function handleClose(alert) {
    setClosing(alert.id);
    const { error } = await supabase
      .from('attacks')
      .update({ status: 'CLOSED' })
      .eq('id', alert.id);
    setClosing(null);
    if (error) {
      toast.error(error.message);
      return;
    }
    toast.success(`Alerta #${alert.id} resuelta`);
    if (statusFilter === 'ACTIVE')
      setItems((prev) => prev.filter((a) => a.id !== alert.id));
    else
      setItems((prev) =>
        prev.map((a) => (a.id === alert.id ? { ...a, status: 'CLOSED' } : a))
      );
  }

  const bySeverity = useMemo(() => {
    const acc = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };
    items.forEach((a) => {
      const s = (a.severity || '').toUpperCase();
      if (acc[s] !== undefined) acc[s] += 1;
    });
    return acc;
  }, [items]);

  return (
    <div className="space-y-5" data-testid="alerts-page">
      {/* Filter bar */}
      <div className="panel p-3 md:p-4 flex flex-col md:flex-row md:items-center gap-3">
        <div className="flex items-center gap-2 mono text-[10px] tracking-widest text-ink-muted">
          <Filter className="w-3.5 h-3.5" />
          FILTROS
        </div>
        <div className="flex flex-wrap gap-1.5">
          {SEVERITIES.map((s) => {
            const active = sevFilter === s;
            const color =
              s === 'ALL'
                ? '#00bfff'
                : SEVERITY_META[s]?.color || '#8a94a6';
            return (
              <button
                key={s}
                data-testid={`filter-sev-${s.toLowerCase()}`}
                onClick={() => setSevFilter(s)}
                className={[
                  'px-2.5 py-1 rounded border mono text-[10px] tracking-widest transition',
                  active
                    ? 'text-black font-semibold'
                    : 'text-ink-dim hover:text-ink border-line/50',
                ].join(' ')}
                style={
                  active
                    ? {
                        background: color,
                        borderColor: color,
                        boxShadow: `0 0 10px ${color}77`,
                      }
                    : {}
                }
              >
                {s}
                {s !== 'ALL' && (
                  <span className="ml-1.5 opacity-70">
                    {bySeverity[s] || 0}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        <div className="hidden md:block w-px h-6 bg-line/40 mx-1" />

        <div className="flex gap-1.5">
          {STATUSES.map((s) => (
            <button
              key={s}
              data-testid={`filter-status-${s.toLowerCase()}`}
              onClick={() => setStatusFilter(s)}
              className={[
                'px-2.5 py-1 rounded border mono text-[10px] tracking-widest transition',
                statusFilter === s
                  ? 'bg-neon-cyan/15 border-neon-cyan/50 text-neon-cyan'
                  : 'border-line/50 text-ink-dim hover:text-ink',
              ].join(' ')}
            >
              {s === 'ACTIVE' ? 'ACTIVAS' : 'TODAS'}
            </button>
          ))}
        </div>

        <div className="relative flex-1 min-w-[180px] md:ml-3">
          <Search className="w-3.5 h-3.5 text-ink-muted absolute left-2.5 top-1/2 -translate-y-1/2" />
          <input
            data-testid="alerts-search"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Buscar IP, tipo o detalles..."
            className="w-full bg-bg-950/70 border border-line/50 rounded pl-8 pr-2 py-1.5 mono text-[12px] text-ink placeholder:text-ink-muted focus:outline-none focus:border-neon-cyan/60"
          />
        </div>

        <select
          data-testid="alerts-sort"
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="bg-bg-950/70 border border-line/50 rounded px-2 py-1.5 mono text-[11px] text-ink"
        >
          <option value="recent">Recientes</option>
          <option value="severity">Severidad</option>
        </select>

        <button
          data-testid="alerts-refresh"
          onClick={load}
          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded border border-line/50 text-ink-dim hover:text-neon-cyan hover:border-neon-cyan/50 transition mono text-[10px] tracking-widest"
        >
          <RefreshCw className={loading ? 'w-3 h-3 animate-spin' : 'w-3 h-3'} />
          RELOAD
        </button>
      </div>

      <div className="panel">
        <div className="panel-heading">
          <span>
            {filtered.length} alerta{filtered.length !== 1 ? 's' : ''}
          </span>
          <span className="text-ink-muted normal-case tracking-normal">
            {sevFilter === 'ALL' ? 'Todas las severidades' : `Severidad: ${sevFilter}`} · {statusFilter === 'ACTIVE' ? 'Solo activas' : 'Todos los estados'}
          </span>
        </div>
        <div className="divide-y divide-line/30 max-h-[calc(100vh-260px)] overflow-y-auto">
          {loading && (
            <div className="p-8 text-center text-ink-dim mono text-xs animate-pulse">
              Cargando...
            </div>
          )}
          {!loading && filtered.length === 0 && (
            <div className="p-10 text-center text-ink-dim">
              <div className="mono text-[12px] tracking-widest">
                SIN RESULTADOS
              </div>
              <div className="text-[13px] mt-1">
                Prueba a cambiar los filtros o esperar nuevos eventos.
              </div>
            </div>
          )}
          {filtered.map((a) => (
            <AlertRow
              key={a.id}
              alert={a}
              onClose={a.status === 'ACTIVE' ? handleClose : null}
              closing={closing === a.id}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
