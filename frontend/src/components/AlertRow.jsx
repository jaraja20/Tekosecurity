import React, { useState } from 'react';
import { severityStyle, timeAgo } from '../lib/format';
import { Zap, X, ChevronRight, ShieldOff } from 'lucide-react';
import BlockIpModal from './BlockIpModal';
import { toast } from 'sonner';

export default function AlertRow({ alert, onClose, closing, compact = false }) {
  const style = severityStyle(alert.severity);
  const sev = (alert.severity || 'LOW').toUpperCase();
  const isCritical = sev === 'CRITICAL';
  const [showBlock, setShowBlock] = useState(false);

  const canBlock = !compact && !!alert.source_ip && alert.status === 'ACTIVE';

  return (
    <>
      <div
        data-testid={`alert-row-${alert.id}`}
        className={[
          'group relative border-l-2 px-4 py-3 hover:bg-line/10 transition',
          'flex items-start gap-4',
          isCritical ? 'animate-slideDown' : '',
        ].join(' ')}
        style={{ borderLeftColor: style.color }}
      >
        <div className="flex-shrink-0 flex flex-col items-center gap-1 pt-0.5">
          <span
            className="chip"
            style={style}
            data-testid={`alert-severity-${alert.id}`}
          >
            {isCritical && <Zap className="w-3 h-3" />}
            {sev}
          </span>
          <span className="mono text-[10px] text-ink-muted tracking-widest">
            #{alert.id}
          </span>
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
            <span className="mono text-[13px] text-ink font-semibold tracking-wide">
              {alert.attack_type}
            </span>
            <span className="mono text-[11px] text-neon-cyan">
              {alert.source_ip || '—'}
            </span>
            {alert.mikrotik_ip && !compact && (
              <span className="mono text-[10px] text-ink-muted">
                via {alert.mikrotik_ip}
              </span>
            )}
            <span className="mono text-[10px] text-ink-muted ml-auto">
              {timeAgo(alert.created_at)}
            </span>
          </div>
          <p className="mt-1 text-[13px] text-ink-dim leading-relaxed line-clamp-2">
            {alert.details || 'Sin detalles'}
          </p>
        </div>

        {!compact && (
          <div className="flex-shrink-0 self-center flex items-center gap-2">
            {canBlock && (
              <button
                data-testid={`block-ip-${alert.id}`}
                onClick={() => setShowBlock(true)}
                title="Bloquear IP en Mikrotik (24h)"
                className="flex items-center gap-1 px-2.5 py-1.5 rounded border border-neon-crit/40 text-neon-crit hover:bg-neon-crit/15 hover:border-neon-crit/70 hover:shadow-glow-crit transition mono text-[10px] tracking-widest"
              >
                <ShieldOff className="w-3 h-3" />
                BLOQUEAR IP
              </button>
            )}
            <button
              data-testid={`close-alert-${alert.id}`}
              onClick={() => onClose && onClose(alert)}
              disabled={closing}
              title="Marcar como resuelta"
              className="flex items-center gap-1 px-2.5 py-1.5 rounded border border-line/50 text-ink-dim hover:text-neon-on hover:border-neon-on/50 hover:bg-neon-on/10 transition mono text-[10px] tracking-widest disabled:opacity-50"
            >
              <X className="w-3 h-3" />
              RESOLVER
            </button>
          </div>
        )}
        {compact && (
          <ChevronRight className="w-4 h-4 text-ink-muted self-center" />
        )}
      </div>

      <BlockIpModal
        alert={alert}
        open={showBlock}
        onClose={() => setShowBlock(false)}
        onDone={(data) => {
          const suf = data.mode === 'DRY_RUN' ? ' (DRY-RUN)' : '';
          toast.success(
            `IP ${alert.source_ip} bloqueada en ${data.locations_blocked?.length || 0} sucursales${suf}`
          );
        }}
      />
    </>
  );
}
