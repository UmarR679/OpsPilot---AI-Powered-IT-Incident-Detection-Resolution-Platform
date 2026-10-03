from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Log(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(20), nullable=False)
    service = db.Column(db.String(100), nullable=False)
    source = db.Column(db.String(100), nullable=True)
    message = db.Column(db.Text, nullable=False)
    anomaly = db.Column(db.Boolean, default=False)
    anomaly_score = db.Column(db.Float, default=0.0)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'level': self.level,
            'service': self.service,
            'source': self.source,
            'message': self.message,
            'anomaly': self.anomaly,
            'anomaly_score': self.anomaly_score,
            'incident_id': self.incident_id
        }

class Incident(db.Model):
    __tablename__ = 'incidents'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    incident_type = db.Column(db.String(50), nullable=False)  # CPU, Memory, Disk, Network, Application, Database, Unknown
    severity = db.Column(db.String(20), nullable=False)       # Low, Medium, High, Critical
    status = db.Column(db.String(30), default='Open')         # Open, Investigating, Resolved
    confidence = db.Column(db.Float, default=0.85)
    root_cause = db.Column(db.Text, nullable=True)
    ai_summary = db.Column(db.Text, nullable=True)
    ai_explanation = db.Column(db.Text, nullable=True)
    remediation = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'incident_type': self.incident_type,
            'severity': self.severity,
            'status': self.status,
            'confidence': round(self.confidence, 2) if self.confidence else 0.85,
            'root_cause': self.root_cause,
            'ai_summary': self.ai_summary,
            'ai_explanation': self.ai_explanation,
            'remediation': self.remediation,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }

class Resolution(db.Model):
    __tablename__ = 'resolutions'

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=False)
    action = db.Column(db.Text, nullable=False)
    result = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    incident = db.relationship('Incident', backref=db.backref('resolutions', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'incident_id': self.incident_id,
            'incident_title': self.incident.title if self.incident else f"Incident #{self.incident_id}",
            'action': self.action,
            'result': self.result,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
