import React from 'react';

export default function MetricCard({
  label,
  value,
  sub,
  accent = '#00bfff',
  icon: Icon,
  testid,
  trend,
}) {
  return (
    <div
      data-testid={testid}
      className="panel p-5 relative overflow-hidden group"
      style={{
        boxShadow: `inset 0 1px 0 rgba(255,255,255,0.03), 0 0 30px ${accent}10`,
      }}
    >
      {/* accent bar */}
      <div
        className="absolute top-0 left-0 h-full w-[3px]"
        style={{ background: accent, boxShadow: `0 0 12px ${accent}` }}
      />

      <div className="flex items-start justify-between">
        <div>
          <div className="mono text-[10px] tracking-[0.24em] text-ink-muted">
            {label}
          </div>
          <div
            className="mt-2 font-semibold mono tabular-nums"
            style={{
              fontSize: 34,
              lineHeight: 1,
              color: accent,
              textShadow: `0 0 18px ${accent}55`,
            }}
            data-testid={testid + '-value'}
          >
            {value}
          </div>
          {sub && (
            <div className="mt-2 mono text-[11px] text-ink-dim">{sub}</div>
          )}
        </div>
        {Icon && (
          <div
            className="w-9 h-9 rounded flex items-center justify-center opacity-70 group-hover:opacity-100 transition"
            style={{
              background: `${accent}12`,
              border: `1px solid ${accent}40`,
            }}
          >
            <Icon className="w-5 h-5" style={{ color: accent }} strokeWidth={1.6} />
          </div>
        )}
      </div>

      {trend && (
        <div className="mt-3 flex items-center gap-2 mono text-[10px] tracking-widest text-ink-muted">
          <div className="h-1 flex-1 bg-line/40 rounded overflow-hidden">
            <div
              className="h-full"
              style={{
                width: `${trend.pct}%`,
                background: accent,
                boxShadow: `0 0 8px ${accent}`,
              }}
            />
          </div>
          <span>{trend.label}</span>
        </div>
      )}
    </div>
  );
}
