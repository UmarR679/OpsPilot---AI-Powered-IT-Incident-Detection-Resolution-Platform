# OpsPilot — AI-Powered IT Incident Detection & Automated Resolution Platform

OpsPilot is an intelligent IT operations platform designed for real-time log ingestion, machine-learning-driven anomaly detection, explainable incident classification, automated root-cause analysis, Google Gemini API integration, and safe simulated remediation.

---

## 🚀 Key Features

1. **Log Ingestion & Parsing**: Upload CSV/JSON log files with automatic SQLite/PostgreSQL storage and pre-packaged realistic sample log datasets.
2. **ML Anomaly Detection**: Uses `Scikit-learn IsolationForest` to analyze log streams, assign anomaly scores, and mark log entries as normal or anomalous.
3. **Incident Classification & Severity Engine**: Automatically groups anomalous logs into CPU, Memory, Disk, Network, Database, Application, or Unknown incident categories, assigning Low, Medium, High, or Critical severity.
4. **Explainable Root Cause Analysis**: Identifies clear, evidence-backed root causes derived from log patterns and service metrics.
5. **Google Gemini API Integration**: Integrates directly with Google Gemini APIs using the official `google-genai` Python SDK via environment variables (`GEMINI_API_KEY`, `GEMINI_MODEL`). Features a graceful offline fallback system if credentials are not configured.
6. **Simulated Resolution Engine**: Safe automated remediation triggers (e.g., simulated service restarts, connection resets) recorded persistently in the database.
7. **Modern React Dashboard**: Clean, minimal, flat UI with real-time metric cards, severity/type distribution charts, status banners, log view, incident filters, and optional dark mode toggle.

---

## 🛠️ Technology Stack

- **Frontend**: React 18, Vite, JavaScript, Lucide Icons, CSS3
- **Backend**: Python 3.11, Flask, Flask-CORS, Flask-SQLAlchemy
- **Database**: PostgreSQL (with SQLite auto-fallback for quick local dev)
- **Machine Learning**: Scikit-learn (`IsolationForest`), Pandas, NumPy
- **AI Integration**: Google Gemini API (`google-genai` SDK)
- **DevOps**: Docker, Docker Compose

---

## 📂 Project Structure

```
OpsPilot/
├── backend/
│   ├── app.py              # Flask app, REST API endpoints, seeding logic
│   ├── config.py           # Configuration & Gemini env settings
│   ├── database.py         # SQLAlchemy models (logs, incidents, resolutions)
│   ├── ml_engine.py        # IsolationForest ML & root-cause engine
│   ├── gemini_service.py   # Google Gemini API integration & offline fallback
│   ├── watsonx_service.py  # Backward compatibility wrapper for gemini_service
│   ├── sample_logs.csv     # Pre-packaged sample log dataset
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend Docker definition
├── frontend/
│   ├── src/
│   │   ├── components/     # MetricCard, SeverityBadge, StatusBadge, Sidebar, Navbar
│   │   ├── pages/          # Dashboard, Incidents, IncidentDetail, Logs, Resolutions
│   │   ├── services/       # Axios API client wrapper
│   │   ├── App.jsx         # Main React routing component
│   │   ├── index.css       # Flat modern UI styling & dark mode styles
│   │   └── main.jsx        # React DOM render entry point
│   ├── package.json        # Node dependencies
│   ├── vite.config.js      # Vite build & proxy settings
│   └── Dockerfile          # Frontend Docker definition (Nginx SPA server)
├── docker-compose.yml      # Orchestrates Postgres, Backend, and Frontend
├── .env.example            # Environment variables reference
└── README.md               # Project documentation
```

---

## 💻 How to Run Locally

### Prerequisites
- Python 3.11+
- Node.js v18+ & npm

### 1. Run Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```
*The Flask backend will run at `http://localhost:5000` and automatically seed the database with sample logs.*

### 2. Run Frontend

```bash
cd frontend
npm install
npm run dev
```
*Open `http://localhost:3000` in your browser.*

---

## 🤖 Google Gemini API Configuration

To enable live Google Gemini foundation model analysis:

1. Create a `.env` file or export the following variables in your environment:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

2. When configured, clicking **"Analyze with Gemini"** on any incident detail page will generate real-time AI incident summaries, technical explanations, and remediation steps directly from Gemini.
3. If credentials are omitted, OpsPilot automatically provides a clear explainable rule-based response (`ai_source: "fallback"`) so all features remain 100% functional.

---

## 📋 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | System health & Gemini configuration status |
| `GET` | `/api/dashboard` | Dashboard metrics, system status, distributions |
| `GET` | `/api/logs` | Fetch stored logs (optional `?anomaly=true/false`) |
| `POST` | `/api/logs/upload` | Upload CSV/JSON log file for ingestion & ML scoring |
| `GET` | `/api/incidents` | List incidents with filters (`severity`, `status`, `type`, `search`) |
| `GET` | `/api/incidents/<id>` | Fetch detailed incident with linked logs & resolution history |
| `POST` | `/api/incidents/<id>/analyze` | Trigger Gemini AI analysis for incident |
| `PUT` | `/api/incidents/<id>/status` | Update incident status (`Open`, `Investigating`, `Resolved`) |
| `POST` | `/api/incidents/<id>/resolve` | Execute simulated resolution action |
| `GET` | `/api/resolutions` | Fetch resolution history logs |
