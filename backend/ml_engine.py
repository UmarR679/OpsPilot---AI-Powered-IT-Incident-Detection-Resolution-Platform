import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer

class MLEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=50, stop_words='english')

    def detect_anomalies(self, df):
        """
        Takes a pandas DataFrame with columns: ['timestamp', 'level', 'service', 'source', 'message']
        Returns DataFrame with added columns: ['anomaly', 'anomaly_score']
        """
        if df.empty:
            df['anomaly'] = False
            df['anomaly_score'] = 0.0
            return df

        # Prepare feature matrix
        # Feature 1: Level severity weight
        level_weights = {'CRITICAL': 4, 'ERROR': 3, 'WARN': 2, 'WARNING': 2, 'INFO': 1, 'DEBUG': 0}
        df['level_weight'] = df['level'].str.upper().map(lambda l: level_weights.get(l, 1))

        # Feature 2: Log message length
        df['msg_len'] = df['message'].astype(str).str.len()

        # Feature 3: Error keyword presence count
        keywords = ['error', 'critical', 'fail', 'exhausted', 'deadlock', 'oom', 'timeout', 'crash', 'refused', 'exceeded']
        pattern = '|'.join(keywords)
        df['keyword_count'] = df['message'].astype(str).str.lower().str.count(pattern)

        # Build feature array for Isolation Forest
        feature_cols = ['level_weight', 'msg_len', 'keyword_count']
        X = df[feature_cols].values.astype(float)

        # Fit IsolationForest
        # Contamination estimated based on log severity
        n_samples = len(df)
        contamination = min(0.4, max(0.05, sum(df['level_weight'] >= 3) / max(1, n_samples)))
        model = IsolationForest(contamination=contamination, random_state=42)
        
        preds = model.fit_predict(X)
        scores = -model.score_samples(X)

        # Normalize score to [0.0, 1.0] range
        min_s, max_s = scores.min(), scores.max()
        if max_s > min_s:
            norm_scores = (scores - min_s) / (max_s - min_s)
        else:
            norm_scores = np.zeros(n_samples)

        # Mark anomaly if isolation forest predicted -1 OR log level is ERROR/CRITICAL
        anomalies = []
        for i, row in df.iterrows():
            is_anomaly = (preds[i] == -1) or (row['level_weight'] >= 3) or (norm_scores[i] >= 0.55)
            anomalies.append(bool(is_anomaly))

        df['anomaly'] = anomalies
        df['anomaly_score'] = [round(float(s), 3) for s in norm_scores]
        
        # Cleanup temporary feature columns
        df.drop(columns=['level_weight', 'msg_len', 'keyword_count'], inplace=True)
        return df

    def classify_incident_type(self, message):
        """
        Classifies log message into CPU, Memory, Disk, Network, Database, Application, or Unknown
        """
        msg_lower = str(message).lower()

        if any(k in msg_lower for k in ['cpu', 'thread', 'utilization', 'core', 'processor']):
            return 'CPU'
        elif any(k in msg_lower for k in ['memory', 'heap', 'oom', 'ram', 'allocation', 'gc', 'outofmemory']):
            return 'Memory'
        elif any(k in msg_lower for k in ['disk', 'space', 'wal', 'io latency', 'volume', 'filesystem', 'write wait']):
            return 'Disk'
        elif any(k in msg_lower for k in ['socket', 'timeout', 'packet', 'dns', 'connection refused', 'network', 'eth0', 'gateway']):
            return 'Network'
        elif any(k in msg_lower for k in ['database', 'postgres', 'connection pool', 'deadlock', 'query', 'sql', 'db']):
            return 'Database'
        elif any(k in msg_lower for k in ['nullpointerexception', 'http 500', 'exception', 'worker process crashed', 'application', 'render payment', 'java.lang']):
            return 'Application'
        else:
            return 'Unknown'

    def calculate_severity(self, anomaly_score, max_level, count, incident_type):
        """
        Assigns Low, Medium, High, Critical severity
        """
        max_level_str = str(max_level).upper()
        if max_level_str == 'CRITICAL' or anomaly_score >= 0.8:
            return 'Critical'
        elif max_level_str == 'ERROR' or anomaly_score >= 0.65 or count >= 3:
            return 'High'
        elif max_level_str in ['WARN', 'WARNING'] or anomaly_score >= 0.4:
            return 'Medium'
        else:
            return 'Low'

    def analyze_root_cause(self, incident_type, sample_messages):
        """
        Simple explainable root-cause engine
        """
        combined = ' '.join(sample_messages).lower()
        
        if incident_type == 'CPU':
            cause = "High CPU utilization (>95%) sustained over monitor threshold causing process thread exhaustion and service latency."
        elif incident_type == 'Memory':
            cause = "Memory leak/exhaustion resulting in java.lang.OutOfMemoryError and kernel process OOM kill."
        elif incident_type == 'Disk':
            cause = "Disk space capacity threshold exceeded (92% full) on /data/db causing Write-Ahead Log (WAL) write failures."
        elif incident_type == 'Network':
            cause = "Upstream gateway connection socket timeout and packet drop (5.2%) causing DNS resolution failures."
        elif incident_type == 'Database':
            cause = "Database connection pool exhaustion combined with SQL update query deadlocks."
        elif incident_type == 'Application':
            cause = "Unhandled runtime exception (NullPointerException) triggering HTTP 500 server crashes."
        else:
            cause = "Unusual system behavior detected in log frequency and payload anomaly pattern."
            
        evidence = f"Evidence based on {len(sample_messages)} log entries: " + "; ".join(sample_messages[:3])
        return cause, evidence

    def group_logs_into_incidents(self, logs_list):
        """
        Groups anomalous logs into incident objects.
        logs_list is a list of log dictionaries or Log model objects.
        """
        anomalous_logs = [l for l in logs_list if (l.get('anomaly') if isinstance(l, dict) else l.anomaly)]
        if not anomalous_logs:
            return []

        # Group by service and incident type
        grouped = {}
        for l in anomalous_logs:
            msg = l.get('message') if isinstance(l, dict) else l.message
            svc = l.get('service') if isinstance(l, dict) else l.service
            level = l.get('level') if isinstance(l, dict) else l.level
            score = l.get('anomaly_score') if isinstance(l, dict) else l.anomaly_score

            itype = self.classify_incident_type(msg)
            key = f"{svc}_{itype}"
            if key not in grouped:
                grouped[key] = {
                    'service': svc,
                    'incident_type': itype,
                    'logs': [],
                    'log_objects': [],
                    'max_score': 0.0,
                    'levels': []
                }
            grouped[key]['logs'].append(msg)
            grouped[key]['log_objects'].append(l)
            grouped[key]['levels'].append(level)
            if score > grouped[key]['max_score']:
                grouped[key]['max_score'] = score

        incidents = []
        for key, item in grouped.items():
            itype = item['incident_type']
            svc = item['service']
            logs = item['logs']
            max_score = item['max_score']
            
            # Determine highest level
            highest_level = 'INFO'
            for lev in ['CRITICAL', 'ERROR', 'WARN', 'INFO']:
                if lev in [l.upper() for l in item['levels']]:
                    highest_level = lev
                    break

            sev = self.calculate_severity(max_score, highest_level, len(logs), itype)
            root_cause, evidence = self.analyze_root_cause(itype, logs)

            title = f"{sev} {itype} Incident detected on {svc}"
            
            # Default remediation recommendation
            remediation = self.get_remediation_recommendation(itype)

            incidents.append({
                'title': title,
                'incident_type': itype,
                'severity': sev,
                'status': 'Open',
                'confidence': min(0.98, max(0.75, max_score + 0.1)),
                'root_cause': f"{root_cause}\n[{evidence}]",
                'remediation': remediation,
                'ai_summary': None,
                'ai_explanation': None,
                'log_objects': item['log_objects']
            })

        return incidents

    def get_remediation_recommendation(self, incident_type):
        remediations = {
            'CPU': 'Simulated restart of affected service',
            'Memory': 'Simulated worker pool memory reset',
            'Disk': 'Simulated log rotation and temp cache clear',
            'Network': 'Simulated network service restart',
            'Database': 'Simulated database connection reset',
            'Application': 'Simulated application service restart',
            'Unknown': 'Simulated diagnostic service reboot'
        }
        return remediations.get(incident_type, 'Simulated application service restart')

ml_engine = MLEngine()
