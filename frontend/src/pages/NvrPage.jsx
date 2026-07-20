import React, { useEffect, useMemo, useState } from 'react';
import { toast } from 'sonner';
import { RefreshCw, Server } from 'lucide-react';
import { supabase } from '../lib/supabase';
import NvrCard from '../components/NvrCard';

export default function NvrPage() {
  const [nvrs, setNvrs] = useState([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    const { data, error } = await supabase
      .from('hikvision_events')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(500);
    if (error) {
      toast.error(error.message);
      setLoading(false);
      return;
    }
    const latest = new Map();
    for (const row of data || []) {
      if (!latest.has(row.nvr_id)) latest.set(row.nvr_id, row);
    }
    setNvrs(Array.from(latest.values()).sort((a, b) => a.nvr_id - b.nvr_id));
    setLoading(false);
  }

  useEffect(() => {
    load();
    const ch = supabase
      .channel('rt-nvrs-page')
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'hikvision_events' },
        () => load()
      )
      .subscribe();
    return () => supabase.removeChannel(ch);
  }, []);

  const groups = useMemo(() => {
    const map = new Map();
    for (const n of nvrs) {
      const key = n.location || 'Sin ubicación';
      if (!map.has(key)) map.set(key, []);
      map.get(key).push(n);
    }
    return Array.from(map.entries());
  }, [nvrs]);

  const online = nvrs.filter((n) => (n.status || '').toUpperCase() === 'ONLINE').length;

  return (
    <div className="space-y-5" data-testid="nvrs-page">
      <div className="panel p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Server className="w-5 h-5 text-neon-cyan" strokeWidth={1.6} />
          <div>
            <div className="mono text-[10px] tracking-widest text-ink-muted">
              INFRAESTRUCTURA HIKVISION
            </div>
            <div className="text-[15px] font-semibold">
              {nvrs.length} NVRs · {online} online · {groups.length} sucursal
              {groups.length !== 1 ? 'es' : ''}
            </div>
          </div>
        </div>
        <button
          data-testid="nvrs-refresh"
          onClick={load}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded border border-line/50 text-ink-dim hover:text-neon-cyan hover:border-neon-cyan/50 transition mono text-[10px] tracking-widest"
        >
          <RefreshCw className={loading ? 'w-3 h-3 animate-spin' : 'w-3 h-3'} />
          RELOAD
        </button>
      </div>

      {loading && nvrs.length === 0 && (
        <div className="panel p-8 text-center text-ink-dim mono text-xs animate-pulse">
          Cargando dispositivos...
        </div>
      )}

      {groups.map(([location, list]) => (
        <section key={location} className="space-y-3">
          <div className="flex items-center gap-3">
            <h2 className="mono text-[11px] tracking-[0.2em] text-ink-dim uppercase">
              {location}
            </h2>
            <div className="flex-1 h-px bg-line/30" />
            <span className="mono text-[10px] tracking-widest text-ink-muted">
              {list.filter((n) => (n.status || '').toUpperCase() === 'ONLINE').length}
              /{list.length}
            </span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {list.map((n) => (
              <NvrCard key={n.nvr_id} nvr={n} />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
