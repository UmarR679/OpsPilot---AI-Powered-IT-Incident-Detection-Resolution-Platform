import React, { useEffect, useState } from 'react';
import { fetchResolutions } from '../services/api';
import { CheckCircle2, ShieldCheck } from 'lucide-react';

export default function ResolutionsPage({ onViewIncident }) {
  const [resolutions, setResolutions] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadResolutions = async () => {
    try {
      setLoading(true);
      const data = await fetchResolutions();
      setResolutions(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadResolutions();
  }, []);

  return (
    <div className="page-body">
      <div className="panel">
        <div className="panel-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldCheck size={20} style={{ color: '#16a34a' }} />
            <h3 className="panel-title">Automated Resolution History ({resolutions.length})</h3>
          </div>
        </div>

        {loading ? (
          <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>Loading resolution logs...</div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Resolution ID</th>
                  <th>Incident ID</th>
                  <th>Incident Title</th>
                  <th>Remediation Action Executed</th>
                  <th>Execution Result</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {resolutions.length === 0 ? (
                  <tr>
                    <td colSpan="6" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No resolution actions executed yet</td>
                  </tr>
                ) : (
                  resolutions.map((res) => (
                    <tr key={res.id}>
                      <td>#{res.id}</td>
                      <td>#{res.incident_id}</td>
                      <td
                        style={{ fontWeight: 600, color: 'var(--primary-color)', cursor: 'pointer' }}
                        onClick={() => onViewIncident(res.incident_id)}
                      >
                        {res.incident_title}
                      </td>
                      <td style={{ fontWeight: 500 }}>{res.action}</td>
                      <td>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: '#15803d', fontSize: '13px' }}>
                          <CheckCircle2 size={14} /> {res.result}
                        </span>
                      </td>
                      <td style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                        {res.created_at ? new Date(res.created_at).toLocaleString() : 'N/A'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
