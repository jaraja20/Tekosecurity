import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// Interceptar fetch global para agregar header de bypass-tunnel-reminder
const originalFetch = window.fetch;
window.fetch = function(...args) {
  const [resource, config = {}] = args;
  const newConfig = {
    ...config,
    headers: {
      'bypass-tunnel-reminder': 'true',
      ...config.headers,
    },
  };
  return originalFetch.apply(this, [resource, newConfig]);
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
