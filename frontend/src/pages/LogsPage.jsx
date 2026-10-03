import React, { useEffect, useState } from 'react';
import { fetchLogs, uploadLogs } from '../services/api';
import { Upload, FileText, AlertTriangle, CheckCircle, RefreshCw } from 'lucide-react';

export default function LogsPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [anomalyOnly, setAnomalyOnly] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);

  const loadLogs = async (anomalyFilter = anomalyOnly) => {
    try {
      setLoading(true);
      const data = await fetchLogs(anomalyFilter);
      setLogs(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs(anomalyOnly);
  }, [anomalyOnly]);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploading(true);
      setUploadStatus(null);
      const res = await uploadLogs(formData);
      setUploadStatus({
        type: 'success',
        text: `Success! Ingested ${res.logs_ingested} logs. Detected ${res.anomalies_detected} anomalies, created ${res.incidents_created} new incidents.`
      });
      loadLogs();
    } catch (err) {
      console.error(err);
      setUploadStatus({
        type: 'error',
        text: err.response?.data?.error || 'Failed to upload log file.'
      });
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  return (
    <div className="page-body">
      {/* Log Ingestion Upload Panel */}
      <div className="panel" style={{ marginBottom: '20px' }}>
        <div className="panel-header">
          <h3 className="panel-title">Log Ingestion Engine</h3>
          <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Supports CSV & JSON log files</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <label className="btn btn-primary" style={{ cursor: 'pointer' }}>
            <Upload size={16} />
            {uploading ? 'Processing Log File...' : 'Upload CSV / JSON Logs'}
            <input
              type="file"
              accept=".csv,.json"
              onChange={handleFileUpload}
              disabled={uploading}
              style={{ display: 'none' }}
            />
          </label>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              className={`btn ${anomalyOnly === null ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setAnomalyOnly(null)}
            >
              All Logs
            </button>
            <button
              className={`btn ${anomalyOnly === true ? 'btn-warning' : 'btn-secondary'}`}
              onClick={() => setAnomalyOnly(true)}
            >
              Anomalies Only
            </button>
            <button
              className={`btn ${anomalyOnly === false ? 'btn-secondary' : 'btn-secondary'}`}
              onClick={() => setAnomalyOnly(false)}
            >
              Normal Only
            </button>
          </div>
        </div>

        {uploadStatus && (
          <div
            className="status-banner"
            style={{
              marginTop: '16px',
              marginBottom: 0,
              backgroundColor: uploadStatus.type === 'error' ? '#fef2f2' : '#f0fdf4',
              color: uploadStatus.type === 'error' ? '#991b1b' : '#166534',
              border: `1px solid ${uploadStatus.type === 'error' ? '#fecaca' : '#bbf7d0'}`
            }}
          >
            {uploadStatus.text}
          </div>
        )}
      </div>

      {/* Logs Table */}
      <div className="panel">
        <div className="panel-header">
          <h3 className="panel-title">Ingested System Logs ({logs.length})</h3>
          <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '12px' }} onClick={() => loadLogs()}>
            <RefreshCw size={14} /> Refresh
          </button>
        </div>

        {loading ? (
          <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>Loading log dataset...</div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Timestamp</th>
                  <th>Level</th>
                  <th>Service</th>
                  <th>Source</th>
                  <th>Message</th>
                  <th>Anomaly Indicator</th>
                </tr>
              </thead>
              <tbody>
                {logs.length === 0 ? (
                  <tr>
                    <td colSpan="7" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No log entries found</td>
                  </tr>
                ) : (
                  logs.map((log) => (
                    <tr key={log.id}>
                      <td>#{log.id}</td>
                      <td style={{ fontSize: '12px', whiteSpace: 'nowrap' }}>{log.timestamp}</td>
                      <td>
                        <span className={`badge ${log.level === 'CRITICAL' ? 'badge-critical' : log.level === 'ERROR' ? 'badge-high' : log.level === 'WARN' ? 'badge-medium' : 'badge-low'}`}>
                          {log.level}
                        </span>
                      </td>
                      <td style={{ fontWeight: 500 }}>{log.service}</td>
                      <td style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{log.source || 'N/A'}</td>
                      <td style={{ fontFamily: 'monospace', fontSize: '13px' }}>{log.message}</td>
                      <td>
                        {log.anomaly ? (
                          <span className="badge badge-critical" title={`Anomaly Score: ${log.anomaly_score}`}>
                            <AlertTriangle size={12} style={{ marginRight: '4px' }} /> Anomaly ({log.anomaly_score})
                          </span>
                        ) : (
                          <span className="badge badge-low">
                            <CheckCircle size={12} style={{ marginRight: '4px' }} /> Normal
                          </span>
                        )}
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
