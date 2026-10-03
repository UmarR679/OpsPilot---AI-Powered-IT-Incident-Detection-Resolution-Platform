import React, { useEffect, useState } from 'react';
import { fetchDashboard } from '../services/api';
import MetricCard from '../components/MetricCard';
import SeverityBadge from '../components/SeverityBadge';
import StatusBadge from '../components/StatusBadge';
import { AlertOctagon, AlertTriangle, CheckCircle, ShieldAlert, Activity, ArrowRight } from 'lucide-react';

export default function DashboardPage({ onViewIncident }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const res = await fetchDashboard();
      setData(res);
      setError(null);
    } catch (err) {
      console.error(err);
      setError('Failed to load dashboard metrics. Ensure backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  if (loading) {
    return <div className="page-body">Loading dashboard analytics...</div>;
  }

  if (error) {
    return (
      <div className="page-body">
        <div className="panel" style={{ color: '#dc2626' }}>
          {error}
          <button className="btn btn-secondary" style={{ marginTop: '12px' }} onClick={loadDashboardData}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  const { metrics, system_status, recent_incidents, severity_distribution, type_distribution } = data;

  const getStatusBannerClass = () => {
    if (system_status === 'Critical Alert') return 'critical';
    if (system_status === 'Degraded Performance') return 'degraded';
    return 'operational';
  };

  return (
    <div className="page-body">
      {/* System Status Banner */}
      <div className={`status-banner ${getStatusBannerClass()}`}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Activity size={20} />
          <span>System Status: <strong>{system_status}</strong></span>
        </div>
        <span style={{ fontSize: '13px' }}>
          {metrics.anomalous_logs} anomaly logs detected from {metrics.total_logs} total records
        </span>
      </div>

      {/* Metrics Row */}
      <div className="metrics-grid">
        <MetricCard
          title="Total Incidents"
          value={metrics.total_incidents}
          icon={AlertOctagon}
          color="#2563eb"
          bg="#eff6ff"
        />
        <MetricCard
          title="Critical"
          value={metrics.critical}
          icon={ShieldAlert}
          color="#dc2626"
          bg="#fef2f2"
        />
        <MetricCard
          title="High"
          value={metrics.high}
          icon={AlertTriangle}
          color="#ea580c"
          bg="#fff7ed"
        />
        <MetricCard
          title="Medium"
          value={metrics.medium}
          icon={AlertTriangle}
          color="#d97706"
          bg="#fefce8"
        />
        <MetricCard
          title="Resolved"
          value={metrics.resolved}
          icon={CheckCircle}
          color="#16a34a"
          bg="#f0fdf4"
        />
      </div>

      {/* Charts & Distribution Panels */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px', marginBottom: '24px' }}>
        
        {/* Severity Distribution */}
        <div className="panel">
          <div className="panel-header">
            <h3 className="panel-title">Severity Distribution</h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {severity_distribution.map((item) => {
              const pct = metrics.total_incidents > 0 ? Math.round((item.count / metrics.total_incidents) * 100) : 0;
              return (
                <div key={item.name}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 500 }}>{item.name}</span>
                    <span style={{ color: 'var(--text-muted)' }}>{item.count} ({pct}%)</span>
                  </div>
                  <div style={{ height: '8px', width: '100%', backgroundColor: 'var(--border-color)', borderRadius: '4px', overflow: 'hidden' }}>
                    <div
                      style={{
                        height: '100%',
                        width: `${pct}%`,
                        backgroundColor: item.name === 'Critical' ? '#dc2626' : item.name === 'High' ? '#ea580c' : item.name === 'Medium' ? '#d97706' : '#16a34a'
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Incident Type Breakdown */}
        <div className="panel">
          <div className="panel-header">
            <h3 className="panel-title">Incident Type Distribution</h3>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
            {type_distribution.map((item) => (
              <div key={item.name} style={{ padding: '12px', border: '1px solid var(--border-color)', borderRadius: '6px', backgroundColor: 'var(--bg-color)' }}>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{item.name}</div>
                <div style={{ fontSize: '20px', fontWeight: '700', marginTop: '2px' }}>{item.count}</div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Recent Incidents Panel */}
      <div className="panel">
        <div className="panel-header">
          <h3 className="panel-title">Recent Detected Incidents</h3>
        </div>
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Type</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Confidence</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {recent_incidents.length === 0 ? (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No incidents recorded</td>
                </tr>
              ) : (
                recent_incidents.map((inc) => (
                  <tr key={inc.id}>
                    <td>#{inc.id}</td>
                    <td style={{ fontWeight: 600 }}>{inc.title}</td>
                    <td>{inc.incident_type}</td>
                    <td><SeverityBadge severity={inc.severity} /></td>
                    <td><StatusBadge status={inc.status} /></td>
                    <td>{(inc.confidence * 100).toFixed(0)}%</td>
                    <td>
                      <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '12px' }} onClick={() => onViewIncident(inc.id)}>
                        View <ArrowRight size={14} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
