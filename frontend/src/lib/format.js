// Format utilities for TEKOSECURE

export const SEVERITY_META = {
  CRITICAL: { color: '#ff1744', label: 'Crítica', bg: '#ffebee' },
  HIGH: { color: '#ff9100', label: 'Alta', bg: '#fff3e0' },
  MEDIUM: { color: '#ffeb3b', label: 'Media', bg: '#fffde7' },
  LOW: { color: '#00ff88', label: 'Baja', bg: '#e8f5e9' },
};

export function severityStyle(severity) {
  return SEVERITY_META[severity?.toUpperCase()] || SEVERITY_META.LOW;
}

export function formatDate(isoString) {
  if (!isoString) return '—';
  return new Date(isoString).toLocaleString('es-PY');
}

export function formatBytes(bytes) {
  if (!bytes) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

export function formatIp(ip) {
  return ip || '—';
}

export function timeAgo(isoString) {
  if (!isoString) return '—';
  const now = new Date();
  const then = new Date(isoString);
  const diff = Math.floor((now - then) / 1000); // segundos

  if (diff < 60) return `hace ${diff}s`;
  if (diff < 3600) return `hace ${Math.floor(diff / 60)}m`;
  if (diff < 86400) return `hace ${Math.floor(diff / 3600)}h`;
  if (diff < 604800) return `hace ${Math.floor(diff / 86400)}d`;
  return formatDate(isoString);
}

export function isSameDay(date1, date2) {
  if (!date1 || !date2) return false;
  const d1 = new Date(date1);
  const d2 = new Date(date2);
  return (
    d1.getFullYear() === d2.getFullYear() &&
    d1.getMonth() === d2.getMonth() &&
    d1.getDate() === d2.getDate()
  );
}
