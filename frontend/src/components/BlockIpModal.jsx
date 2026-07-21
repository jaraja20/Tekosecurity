import React, { useState } from 'react';
import { ShieldOff, X, AlertTriangle, Loader2 } from 'lucide-react';
import { supabase } from '../lib/supabase';

const BACKEND = process.env.REACT_APP_BACKEND_URL?.replace(/\/$/, '') || '';

/**
 * Modal + trigger button used to invoke /api/actions/block-ip-real.
 * The button itself is not rendered — the parent renders BlockIpButton
 * which owns the confirm dialog state. We keep this pure so it plays
 * well with AlertRow.
 */
export default function BlockIpModal({ alert, open, onClose, onDone }) {
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  if (!open) return null;

  async function confirm() {
    setBusy(true);
    setError('');
    setResult(null);
    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (!session) throw new Error('Sesión expirada. Vuelve a iniciar sesión.');

      const r = await fetch(`${BACKEND}/api/actions/block-ip-real`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({
          attack_id: alert.id,
          source_ip: alert.source_ip,
          reason: alert.attack_type || 'attack',
        }),
      });
      const data = await r.json();
      if (!r.ok || data.success === false) {
        throw new Error(data.detail || data.message || 'Error desconocido');
      }
      setResult(data);
      if (onDone) onDone(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div
      data-testid="block-ip-modal"
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={busy ? undefined : onClose}
      />
      <div className="relative panel w-full max-w-lg p-6 border-neon-crit/40 shadow-[0_0_60px_rgba(255,23,68,0.25)]">
        <button
          onClick={onClose}
          disabled={busy}
          className="absolute top-3 right-3 text-ink-muted hover:text-ink disabled:opacity-40"
          data-testid="block-ip-close"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-3 mb-4">
          <div className="w-11 h-11 rounded-md border border-neon-crit/50 bg-neon-crit/10 flex items-center justify-center shadow-glow-crit">
            <ShieldOff className="w-6 h-6 text-neon-crit" strokeWidth={1.6} />
          </div>
          <div>
            <div className="mono text-[10px] tracking-[0.28em] text-ink-muted">
              ACCIÓN CRÍTICA
            </div>
            <h2 className="text-xl font-semibold tracking-tight">
              Bloquear IP en Mikrotik
            </h2>
          </div>
        </div>

        {!result && (
          <>
            <div className="rounded border border-line/50 bg-bg-950/70 p-3 mono text-[12px] space-y-1 mb-4">
              <div className="flex gap-2">
                <span className="text-ink-muted w-24">IP:</span>
                <span className="text-neon-cyan">{alert.source_ip}</span>
              </div>
              <div className="flex gap-2">
                <span className="text-ink-muted w-24">Ataque:</span>
                <span className="text-ink">{alert.attack_type}</span>
              </div>
              <div className="flex gap-2">
                <span className="text-ink-muted w-24">Severidad:</span>
                <span className="text-ink">{alert.severity}</span>
              </div>
              <div className="flex gap-2">
                <span className="text-ink-muted w-24">Attack #:</span>
                <span className="text-ink-dim">{alert.id}</span>
              </div>
            </div>

            <div className="flex items-start gap-2 rounded border border-neon-high/40 bg-neon-high/5 p-3 text-[12px] text-ink-dim mb-5">
              <AlertTriangle className="w-4 h-4 text-neon-high flex-shrink-0 mt-0.5" />
              <p className="leading-relaxed">
                Se añadirán reglas <code className="mono text-neon-cyan">drop</code> en{' '}
                <span className="mono text-ink">INPUT</span> y{' '}
                <span className="mono text-ink">FORWARD</span> en las <strong>4 sucursales</strong>{' '}
                (MATRIZ_KM6, OASIS, KM12, HERNANDARIAS) con{' '}
                <span className="mono text-neon-cyan">timeout=24h</span>. Reversible sin reinicio.
              </p>
            </div>

            {error && (
              <div
                data-testid="block-ip-error"
                className="rounded border border-neon-crit/50 bg-neon-crit/10 text-neon-crit p-3 mono text-[12px] mb-4"
              >
                {error}
              </div>
            )}

            <div className="flex gap-2 justify-end">
              <button
                onClick={onClose}
                disabled={busy}
                data-testid="block-ip-cancel"
                className="px-4 py-2 rounded border border-line/50 hover:border-ink-dim text-ink-dim hover:text-ink mono text-[11px] tracking-widest transition disabled:opacity-50"
              >
                CANCELAR
              </button>
              <button
                onClick={confirm}
                disabled={busy}
                data-testid="block-ip-confirm"
                className="px-4 py-2 rounded border border-neon-crit/50 bg-neon-crit/15 hover:bg-neon-crit/25 text-neon-crit mono text-[11px] tracking-widest transition shadow-glow-crit disabled:opacity-60 flex items-center gap-2"
              >
                {busy && <Loader2 className="w-3 h-3 animate-spin" />}
                {busy ? 'BLOQUEANDO…' : '// BLOQUEAR 24H'}
              </button>
            </div>
          </>
        )}

        {result && (
          <div data-testid="block-ip-result" className="space-y-3">
            <div className="rounded border border-neon-on/40 bg-neon-on/5 p-3 mono text-[12px] text-neon-on">
              {result.message}
            </div>
            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <div className="rounded border border-line/50 bg-bg-950/70 p-2">
                <div className="mono text-[9px] tracking-widest text-ink-muted">MODO</div>
                <div className="mono text-ink">{result.mode}</div>
              </div>
              <div className="rounded border border-line/50 bg-bg-950/70 p-2">
                <div className="mono text-[9px] tracking-widest text-ink-muted">EXPIRA</div>
                <div className="mono text-ink">{result.expires_in_hours}h</div>
              </div>
              <div className="col-span-2 rounded border border-line/50 bg-bg-950/70 p-2">
                <div className="mono text-[9px] tracking-widest text-ink-muted">
                  SUCURSALES BLOQUEADAS ({result.locations_blocked?.length || 0})
                </div>
                <div className="mono text-ink text-[11px] mt-1">
                  {(result.locations_blocked || []).join(', ') || '—'}
                </div>
              </div>
              {result.locations_failed?.length > 0 && (
                <div className="col-span-2 rounded border border-neon-crit/40 bg-neon-crit/5 p-2">
                  <div className="mono text-[9px] tracking-widest text-neon-crit">
                    FALLIDAS
                  </div>
                  <div className="mono text-neon-crit text-[11px] mt-1">
                    {result.locations_failed.join(', ')}
                  </div>
                </div>
              )}
              {result.locations_unreachable?.length > 0 && (
                <div className="col-span-2 rounded border border-neon-high/40 bg-neon-high/5 p-2">
                  <div className="mono text-[9px] tracking-widest text-neon-high">
                    NO ALCANZABLES
                  </div>
                  <div className="mono text-neon-high text-[11px] mt-1">
                    {result.locations_unreachable.join(', ')}
                  </div>
                </div>
              )}
            </div>
            <div className="flex justify-end">
              <button
                onClick={onClose}
                data-testid="block-ip-done"
                className="px-4 py-2 rounded border border-neon-cyan/50 bg-neon-cyan/10 text-neon-cyan mono text-[11px] tracking-widest hover:bg-neon-cyan/20"
              >
                CERRAR
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
