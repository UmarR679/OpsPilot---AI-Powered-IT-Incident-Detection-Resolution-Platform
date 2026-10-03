import React from 'react';

export default function MetricCard({ title, value, icon: Icon, color = '#2563eb', bg = '#eff6ff' }) {
  return (
    <div className="metric-card">
      <div className="metric-info">
        <h4>{title}</h4>
        <div className="metric-value">{value}</div>
      </div>
      {Icon && (
        <div className="metric-icon-box" style={{ backgroundColor: bg, color: color }}>
          <Icon size={22} />
        </div>
      )}
    </div>
  );
}
