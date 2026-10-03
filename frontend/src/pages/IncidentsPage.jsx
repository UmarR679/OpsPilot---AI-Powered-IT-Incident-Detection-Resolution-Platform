import React, { useEffect, useState } from 'react';
import { fetchIncidents } from '../services/api';
import SeverityBadge from '../components/SeverityBadge';
import StatusBadge from '../components/StatusBadge';
import { Search, Eye, Filter } from 'lucide-react';

export default function IncidentsPage({ onViewIncident }) {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters state
  const [search, setSearch] = useState('');
  const [severity, setSeverity] = useState('all');
  const [status, setStatus] = useState('all');
  const [type, setType] = useState('all');

  const loadIncidents = async () => {
    try {
      setLoading(true);
      const data = await fetchIncidents({ search, severity, status, type });
      setIncidents(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadIncidents();
  }, [severity, status, type]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadIncidents();
  };

  return (
    <div className="page-body">
      {/* Filters Bar */}
      <div className="panel" style={{ marginBottom: '20px' }}>
        <form onSubmit={handleSearchSubmit} className="filters-bar" style={{ margin: 0 }}>
          <div style={{ position: 'relative', flex: 1, minWidth: '220px' }}>
            <input
              type="text"
              className="input-text"
              placeholder="Search incidents by title, root cause..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ width: '100%', paddingLeft: '36px' }}
            />
            <Search size={16} style={{ position: 'absolute', left: '12px', top: '10px', color: 'var(--text-muted)' }} />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Filter size={16} style={{ color: 'var(--text-muted)' }} />
            <select className="select-input" value={severity} onChange={(e) => setSeverity(e.target.value)}>
              <option value="all">All Severities</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>

            <select className="select-input" value={status} onChange={(e) => setStatus(e.target.value)}>
              <option value="all">All Statuses</option>
              <option value="Open">Open</option>
              <option value="Investigating">Investigating</option>
              <option value="Resolved">Resolved</option>
            </select>

            <select className="select-input" value={type} onChange={(e) => setType(e.target.value)}>
              <option value="all">All Types</option>
              <option value="CPU">CPU</option>
              <option value="Memory">Memory</option>
              <option value="Disk">Disk</option>
              <option value="Network">Network</option>
              <option value="Database">Database</option>
              <option value="Application">Application</option>
              <option value="Unknown">Unknown</option>
            </select>

            <button type="submit" className="btn btn-primary">
              Search
            </button>
          </div>
        </form>
      </div>

      {/* Incidents Table */}
      <div className="panel">
        <div className="panel-header">
          <h3 className="panel-title">Incidents ({incidents.length})</h3>
        </div>

        {loading ? (
          <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>Loading incidents...</div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Incident Title</th>
                  <th>Type</th>
                  <th>Severity</th>
                  <th>Status</th>
                  <th>Confidence</th>
                  <th>Created At</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {incidents.length === 0 ? (
                  <tr>
                    <td colSpan="8" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No matching incidents found</td>
                  </tr>
                ) : (
                  incidents.map((inc) => (
                    <tr key={inc.id}>
                      <td>#{inc.id}</td>
                      <td style={{ fontWeight: 600 }}>{inc.title}</td>
                      <td>{inc.incident_type}</td>
                      <td><SeverityBadge severity={inc.severity} /></td>
                      <td><StatusBadge status={inc.status} /></td>
                      <td>{(inc.confidence * 100).toFixed(0)}%</td>
                      <td style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                        {inc.created_at ? new Date(inc.created_at).toLocaleString() : 'N/A'}
                      </td>
                      <td>
                        <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '12px' }} onClick={() => onViewIncident(inc.id)}>
                          <Eye size={14} /> View
                        </button>
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
