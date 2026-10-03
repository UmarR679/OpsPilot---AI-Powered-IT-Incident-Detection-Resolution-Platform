import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import DashboardPage from './pages/DashboardPage';
import IncidentsPage from './pages/IncidentsPage';
import IncidentDetailPage from './pages/IncidentDetailPage';
import LogsPage from './pages/LogsPage';
import ResolutionsPage from './pages/ResolutionsPage';

export default function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [selectedIncidentId, setSelectedIncidentId] = useState(null);
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.add('dark');
    } else {
      document.body.classList.remove('dark');
    }
  }, [isDarkMode]);

  const toggleDarkMode = () => setIsDarkMode((prev) => !prev);

  const handleViewIncident = (id) => {
    setSelectedIncidentId(id);
    setCurrentPage('incident-detail');
  };

  const renderContent = () => {
    switch (currentPage) {
      case 'dashboard':
        return <DashboardPage onViewIncident={handleViewIncident} />;
      case 'incidents':
        return <IncidentsPage onViewIncident={handleViewIncident} />;
      case 'incident-detail':
        return (
          <IncidentDetailPage
            incidentId={selectedIncidentId}
            onBack={() => setCurrentPage('incidents')}
          />
        );
      case 'logs':
        return <LogsPage />;
      case 'resolutions':
        return <ResolutionsPage onViewIncident={handleViewIncident} />;
      default:
        return <DashboardPage onViewIncident={handleViewIncident} />;
    }
  };

  const getPageTitle = () => {
    switch (currentPage) {
      case 'dashboard': return { title: 'Executive Overview', subtitle: 'Real-time IT infrastructure status & AI incident insights' };
      case 'incidents': return { title: 'Incident Management', subtitle: 'Filter, inspect, and analyze system anomalies' };
      case 'incident-detail': return { title: 'Incident Analysis & Remediation', subtitle: 'Detailed root-cause inspection and Google Gemini AI summary' };
      case 'logs': return { title: 'Log Ingestion Engine', subtitle: 'Upload and inspect parsed system logs & IsolationForest scores' };
      case 'resolutions': return { title: 'Automated Remediation Audit', subtitle: 'Historical record of simulated resolution actions' };
      default: return { title: 'OpsPilot Platform', subtitle: '' };
    }
  };

  const { title, subtitle } = getPageTitle();

  return (
    <div className="app-layout">
      <Sidebar
        currentPage={currentPage}
        setCurrentPage={(page) => {
          setSelectedIncidentId(null);
          setCurrentPage(page);
        }}
        isDarkMode={isDarkMode}
        toggleDarkMode={toggleDarkMode}
      />
      <main className="main-content">
        <Navbar title={title} subtitle={subtitle} />
        {renderContent()}
      </main>
    </div>
  );
}
