import React from 'react';
import { Video, MapPin, HardDrive, Radio } from 'lucide-react';
import { timeAgo } from '../lib/format';

export default function NvrCard({ nvr }) {
  const isOnline = (nvr.status || '').toUpperCase() === 'ONLINE';
  const accent = isOnline ? '#00ff88' : '#ff0040';

  return (
    <div
      data-testid={`nvr-card-${nvr.nvr_id}`}
      className="panel p-4 relative overflow-hidden transition hover:border-neon-cyan/40"
      style={{
        boxShadow: `inset 0 0 0 1px ${accent}20`,
      }}
    >
      <div
        className="absolute inset-x-0 top-0 h-[2px]"
        style={{
          background: accent,
          boxShadow: `0 0 12px ${accent}`,
        }}
      />

      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <Video className="w-4 h-4 text-neon-cyan" strokeWidth={1.6} />
            <h3
              className="text-[14px] font-semibold tracking-tight truncate"
              data-testid={`nvr-name-${nvr.nvr_id}`}
            >
              {nvr.nvr_name}
            </h3>
          </div>
          <div className="mt-0.5 flex items-center gap-1.5 mono text-[10px] text-ink-muted">
            <MapPin className="w-3 h-3" />
            <span className="truncate">{nvr.location}</span>
          </div>
        </div>

        <div
          className="flex-shrink-0 flex items-center gap-1.5 px-2 py-1 rounded mono text-[10px] tracking-widest font-semibold"
          style={{
            color: accent,
            background: `${accent}12`,
            border: `1px solid ${accent}55`,
            boxShadow: isOnline ? `0 0 8px ${accent}55` : 'none',
          }}
          data-testid={`nvr-status-${nvr.nvr_id}`}
        >
          <span
            className="dot"
            style={{
              background: accent,
              boxShadow: `0 0 6px ${accent}`,
              animation: isOnline ? 'pulseGlow 1.6s ease-in-out infinite' : 'none',
            }}
          />
          {isOnline ? 'ONLINE' : 'OFFLINE'}
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 text-[11px]">
        <div>
          <div className="mono text-[9px] tracking-widest text-ink-muted">IP</div>
          <div className="mono text-ink" data-testid={`nvr-ip-${nvr.nvr_id}`}>
            {nvr.nvr_ip}
          </div>
        </div>
        <div>
          <div className="mono text-[9px] tracking-widest text-ink-muted">
            PUERTOS
          </div>
          <div className="mono text-ink flex items-center gap-1.5">
            <HardDrive className="w-3 h-3 text-ink-dim" />
            {nvr.port_count}
          </div>
        </div>
        <div className="col-span-2">
          <div className="mono text-[9px] tracking-widest text-ink-muted">
            MODELO
          </div>
          <div className="mono text-[11px] text-ink-dim truncate">{nvr.model}</div>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-line/40 flex items-center justify-between mono text-[10px] tracking-widest">
        <span className="flex items-center gap-1.5 text-ink-muted">
          <Radio className="w-3 h-3" />
          Última señal
        </span>
        <span className="text-ink-dim">{timeAgo(nvr.created_at)}</span>
      </div>
    </div>
  );
}
