import React from 'react';

export default function Navbar({ title, subtitle }) {
  return (
    <header className="top-navbar">
      <div>
        <h1 className="page-title">{title}</h1>
        {subtitle && <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{subtitle}</p>}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <span style={{ fontSize: '12px', padding: '4px 10px', borderRadius: '12px', backgroundColor: 'var(--surface-hover)', border: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
          Environment: Production
        </span>
      </div>
    </header>
  );
}
