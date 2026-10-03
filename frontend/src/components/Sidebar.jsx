import React from 'react';
import { LayoutDashboard, AlertTriangle, FileText, CheckCircle2, ShieldCheck, Sun, Moon } from 'lucide-react';

export default function Sidebar({ currentPage, setCurrentPage, isDarkMode, toggleDarkMode }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'incidents', label: 'Incidents', icon: AlertTriangle },
    { id: 'logs', label: 'Logs', icon: FileText },
    { id: 'resolutions', label: 'Resolutions', icon: CheckCircle2 }
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand-icon">
          <ShieldCheck size={20} />
        </div>
        <div>
          <div className="brand-title">OpsPilot</div>
          <div className="brand-subtitle">AI Incident Platform</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <div
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setCurrentPage(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </div>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Theme</span>
        <button className="theme-toggle" onClick={toggleDarkMode} title="Toggle Light/Dark Theme">
          {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </aside>
  );
}
