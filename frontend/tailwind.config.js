/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}', './public/index.html'],
  theme: {
    extend: {
      colors: {
        bg: {
          950: '#050818',
          900: '#0a0e27',
          800: '#0f1533',
          700: '#141b3f',
        },
        line: {
          DEFAULT: '#1e3a8a',
          soft: '#1e2a5c',
        },
        neon: {
          crit: '#ff1744',
          high: '#ff9100',
          med: '#ffeb3b',
          low: '#4ade80',
          on: '#00ff88',
          off: '#ff0040',
          cyan: '#00bfff',
        },
        ink: {
          DEFAULT: '#e0e6ed',
          dim: '#8a94a6',
          muted: '#5a6478',
        },
      },
      fontFamily: {
        mono: ['"Roboto Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'glow-crit': '0 0 12px rgba(255,23,68,0.55), 0 0 2px rgba(255,23,68,0.9)',
        'glow-high': '0 0 12px rgba(255,145,0,0.5)',
        'glow-cyan': '0 0 12px rgba(0,191,255,0.4)',
        'glow-on': '0 0 10px rgba(0,255,136,0.55)',
        'glow-off': '0 0 10px rgba(255,0,64,0.55)',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.55 },
        },
        blink: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.35 },
        },
        slideDown: {
          '0%': { transform: 'translateY(-8px)', opacity: 0 },
          '100%': { transform: 'translateY(0)', opacity: 1 },
        },
      },
      animation: {
        pulseGlow: 'pulseGlow 1.6s ease-in-out infinite',
        blink: 'blink 1.2s ease-in-out infinite',
        slideDown: 'slideDown 250ms ease-out',
      },
    },
  },
  plugins: [],
};
