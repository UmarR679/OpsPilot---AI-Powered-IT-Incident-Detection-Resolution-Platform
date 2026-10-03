import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const fetchHealth = async () => {
  const res = await api.get('/health');
  return res.data;
};

export const fetchDashboard = async () => {
  const res = await api.get('/dashboard');
  return res.data;
};

export const fetchLogs = async (anomalyFilter = null) => {
  const params = {};
  if (anomalyFilter !== null) {
    params.anomaly = anomalyFilter;
  }
  const res = await api.get('/logs', { params });
  return res.data;
};

export const uploadLogs = async (formData) => {
  const res = await api.post('/logs/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  return res.data;
};

export const fetchIncidents = async (filters = {}) => {
  const params = {};
  if (filters.severity && filters.severity !== 'all') params.severity = filters.severity;
  if (filters.status && filters.status !== 'all') params.status = filters.status;
  if (filters.type && filters.type !== 'all') params.type = filters.type;
  if (filters.search) params.search = filters.search;

  const res = await api.get('/incidents', { params });
  return res.data;
};

export const fetchIncidentById = async (id) => {
  const res = await api.get(`/incidents/${id}`);
  return res.data;
};

export const analyzeIncidentWithGemini = async (id) => {
  const res = await api.post(`/incidents/${id}/analyze`);
  return res.data;
};

// Backward compatible export alias
export const analyzeIncidentWithWatsonx = analyzeIncidentWithGemini;

export const updateIncidentStatus = async (id, status) => {
  const res = await api.put(`/incidents/${id}/status`, { status });
  return res.data;
};

export const resolveIncident = async (id, action = null) => {
  const res = await api.post(`/incidents/${id}/resolve`, { action });
  return res.data;
};

export const fetchResolutions = async () => {
  const res = await api.get('/resolutions');
  return res.data;
};
