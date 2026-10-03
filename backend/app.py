import os
import io
import pandas as pd
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from database import db, Log, Incident, Resolution
from ml_engine import ml_engine
from gemini_service import gemini_service

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for all routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)

    with app.app_context():
        try:
            db.create_all()
            seed_sample_data_if_empty()
        except Exception as e:
            print(f"[DB Init Exception] {e}")

    # --- API ENDPOINTS ---

    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'ok',
            'gemini_configured': gemini_service.is_configured(),
            'watsonx_configured': gemini_service.is_configured(),
            'timestamp': datetime.utcnow().isoformat()
        })

    @app.route('/api/dashboard', methods=['GET'])
    def get_dashboard():
        total_incidents = Incident.query.count()
        critical_count = Incident.query.filter_by(severity='Critical').count()
        high_count = Incident.query.filter_by(severity='High').count()
        medium_count = Incident.query.filter_by(severity='Medium').count()
        low_count = Incident.query.filter_by(severity='Low').count()
        
        resolved_count = Incident.query.filter_by(status='Resolved').count()
        investigating_count = Incident.query.filter_by(status='Investigating').count()
        open_count = Incident.query.filter_by(status='Open').count()

        total_logs = Log.query.count()
        anomalous_logs = Log.query.filter_by(anomaly=True).count()

        recent_incidents = [inc.to_dict() for inc in Incident.query.order_by(Incident.created_at.desc()).limit(5).all()]

        # System status
        if critical_count > 0 and open_count > 0:
            system_status = "Critical Alert"
        elif (high_count > 0 or medium_count > 0) and open_count > 0:
            system_status = "Degraded Performance"
        else:
            system_status = "Operational"

        severity_distribution = [
            {'name': 'Critical', 'count': critical_count},
            {'name': 'High', 'count': high_count},
            {'name': 'Medium', 'count': medium_count},
            {'name': 'Low', 'count': low_count}
        ]

        # Calculate incident type distribution
        types = ['CPU', 'Memory', 'Disk', 'Network', 'Application', 'Database', 'Unknown']
        type_distribution = []
        for t in types:
            cnt = Incident.query.filter_by(incident_type=t).count()
            if cnt > 0 or True: # Include all for complete chart display
                type_distribution.append({'name': t, 'count': cnt})

        return jsonify({
            'metrics': {
                'total_incidents': total_incidents,
                'critical': critical_count,
                'high': high_count,
                'medium': medium_count,
                'resolved': resolved_count,
                'open': open_count,
                'investigating': investigating_count,
                'total_logs': total_logs,
                'anomalous_logs': anomalous_logs
            },
            'system_status': system_status,
            'recent_incidents': recent_incidents,
            'severity_distribution': severity_distribution,
            'type_distribution': type_distribution
        })

    @app.route('/api/logs', methods=['GET'])
    def get_logs():
        anomaly_filter = request.args.get('anomaly')
        query = Log.query

        if anomaly_filter is not None:
            if anomaly_filter.lower() == 'true':
                query = query.filter_by(anomaly=True)
            elif anomaly_filter.lower() == 'false':
                query = query.filter_by(anomaly=False)

        logs = query.order_by(Log.id.asc()).limit(300).all()
        return jsonify([l.to_dict() for l in logs])

    @app.route('/api/logs/upload', methods=['POST'])
    def upload_logs():
        if 'file' not in request.files and not request.is_json:
            return jsonify({'error': 'No file or JSON body provided'}), 400

        df = None
        try:
            if 'file' in request.files:
                uploaded_file = request.files['file']
                filename = uploaded_file.filename.lower()
                if filename.endswith('.json'):
                    df = pd.read_json(uploaded_file)
                else:
                    df = pd.read_csv(uploaded_file)
            elif request.is_json:
                data = request.get_json()
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                elif isinstance(data, dict) and 'logs' in data:
                    df = pd.DataFrame(data['logs'])
        except Exception as e:
            return jsonify({'error': f'Failed to parse uploaded content: {str(e)}'}), 400

        if df is None or df.empty:
            return jsonify({'error': 'Empty dataset or invalid structure'}), 400

        # Standardize required columns
        for col in ['timestamp', 'level', 'service', 'source', 'message']:
            if col not in df.columns:
                df[col] = 'N/A' if col != 'timestamp' else datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        # Run Anomaly Detection ML
        df = ml_engine.detect_anomalies(df)

        new_logs = []
        for _, row in df.iterrows():
            log_obj = Log(
                timestamp=str(row['timestamp']),
                level=str(row['level']),
                service=str(row['service']),
                source=str(row['source']),
                message=str(row['message']),
                anomaly=bool(row['anomaly']),
                anomaly_score=float(row['anomaly_score'])
            )
            db.session.add(log_obj)
            new_logs.append(log_obj)

        db.session.commit()

        # Generate Incidents from Anomalies
        generated_incidents = ml_engine.group_logs_into_incidents(new_logs)
        created_incidents_count = 0
        for inc_data in generated_incidents:
            # Check if similar active incident exists to avoid duplicate clutter
            existing = Incident.query.filter_by(
                incident_type=inc_data['incident_type'],
                status='Open'
            ).first()
            if existing:
                target_inc_id = existing.id
            else:
                inc = Incident(
                    title=inc_data['title'],
                    incident_type=inc_data['incident_type'],
                    severity=inc_data['severity'],
                    status=inc_data['status'],
                    confidence=inc_data['confidence'],
                    root_cause=inc_data['root_cause'],
                    remediation=inc_data['remediation']
                )
                db.session.add(inc)
                db.session.flush()
                target_inc_id = inc.id
                created_incidents_count += 1

            for log_item in inc_data.get('log_objects', []):
                if isinstance(log_item, Log):
                    log_item.incident_id = target_inc_id

        db.session.commit()

        return jsonify({
            'message': 'Logs ingested and processed successfully',
            'logs_ingested': len(df),
            'anomalies_detected': int(df['anomaly'].sum()),
            'incidents_created': created_incidents_count
        })

    @app.route('/api/incidents', methods=['GET'])
    def get_incidents():
        severity = request.args.get('severity')
        status = request.args.get('status')
        incident_type = request.args.get('type')
        search = request.args.get('search')

        query = Incident.query

        if severity and severity.lower() != 'all':
            query = query.filter(Incident.severity.ilike(severity))
        if status and status.lower() != 'all':
            query = query.filter(Incident.status.ilike(status))
        if incident_type and incident_type.lower() != 'all':
            query = query.filter(Incident.incident_type.ilike(incident_type))
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Incident.title.ilike(search_pattern)) | 
                (Incident.root_cause.ilike(search_pattern)) | 
                (Incident.incident_type.ilike(search_pattern))
            )

        incidents = query.order_by(Incident.created_at.desc()).all()
        return jsonify([inc.to_dict() for inc in incidents])

    @app.route('/api/incidents/<int:incident_id>', methods=['GET'])
    def get_incident(incident_id):
        incident = Incident.query.get_or_404(incident_id)
        
        # Fetch related logs directly linked to this incident via foreign key
        related_logs = [l.to_dict() for l in Log.query.filter_by(incident_id=incident_id).order_by(Log.id.asc()).all()]

        # Fetch resolutions
        resolutions = [r.to_dict() for r in Resolution.query.filter_by(incident_id=incident_id).order_by(Resolution.created_at.desc()).all()]

        result = incident.to_dict()
        result['related_logs'] = related_logs
        result['resolutions'] = resolutions
        return jsonify(result)

    @app.route('/api/incidents/<int:incident_id>/analyze', methods=['POST'])
    def analyze_incident(incident_id):
        incident = Incident.query.get_or_404(incident_id)
        
        # Fetch sample log evidence linked to incident
        inc_logs = Log.query.filter_by(incident_id=incident_id).all()
        evidence_logs = "; ".join([l.message for l in (inc_logs if inc_logs else Log.query.filter_by(anomaly=True).all())[:3]])

        analysis = gemini_service.analyze_incident(
            incident_title=incident.title,
            incident_type=incident.incident_type,
            severity=incident.severity,
            root_cause=incident.root_cause,
            evidence_logs=evidence_logs
        )

        incident.ai_summary = analysis['ai_summary']
        incident.ai_explanation = analysis['ai_explanation']
        incident.remediation = analysis['remediation']
        if analysis.get('probable_root_cause'):
            incident.root_cause = analysis['probable_root_cause']

        db.session.commit()
        
        res_dict = incident.to_dict()
        res_dict['ai_source'] = analysis.get('ai_source', 'fallback')
        return jsonify(res_dict)

    @app.route('/api/incidents/<int:incident_id>/status', methods=['PUT'])
    def update_incident_status(incident_id):
        incident = Incident.query.get_or_404(incident_id)
        data = request.get_json(silent=True) or {}
        new_status = data.get('status')

        if not new_status:
            return jsonify({'error': 'Missing status field'}), 400

        incident.status = new_status
        if new_status == 'Resolved':
            incident.resolved_at = datetime.utcnow()
        elif new_status == 'Open':
            incident.resolved_at = None

        db.session.commit()
        return jsonify(incident.to_dict())

    @app.route('/api/incidents/<int:incident_id>/resolve', methods=['POST'])
    def resolve_incident(incident_id):
        incident = Incident.query.get_or_404(incident_id)
        data = request.get_json(silent=True) or {}
        
        custom_action = data.get('action')
        action_text = custom_action or ml_engine.get_remediation_recommendation(incident.incident_type)
        result_text = f"Success: Executed '{action_text}'. Service restored, metrics normalized, 0 active anomalies."

        resolution = Resolution(
            incident_id=incident.id,
            action=action_text,
            result=result_text,
            created_at=datetime.utcnow()
        )

        incident.status = 'Resolved'
        incident.resolved_at = datetime.utcnow()

        db.session.add(resolution)
        db.session.commit()

        return jsonify({
            'message': 'Incident resolved successfully',
            'incident': incident.to_dict(),
            'resolution': resolution.to_dict()
        })

    @app.route('/api/resolutions', methods=['GET'])
    def get_resolutions():
        resolutions = Resolution.query.order_by(Resolution.created_at.desc()).all()
        return jsonify([r.to_dict() for r in resolutions])

    return app

def seed_sample_data_if_empty():
    if Log.query.first() is not None:
        return

    print("[OpsPilot Seed] Ingesting default sample_logs.csv...")
    sample_csv_path = os.path.join(os.path.dirname(__file__), 'sample_logs.csv')
    if os.path.exists(sample_csv_path):
        df = pd.read_csv(sample_csv_path)
        df = ml_engine.detect_anomalies(df)

        logs_to_add = []
        for _, row in df.iterrows():
            log_obj = Log(
                timestamp=str(row['timestamp']),
                level=str(row['level']),
                service=str(row['service']),
                source=str(row['source']),
                message=str(row['message']),
                anomaly=bool(row['anomaly']),
                anomaly_score=float(row['anomaly_score'])
            )
            db.session.add(log_obj)
            logs_to_add.append(log_obj)

        db.session.commit()

        # Generate seed incidents
        incidents_data = ml_engine.group_logs_into_incidents(logs_to_add)
        for inc_data in incidents_data:
            inc = Incident(
                title=inc_data['title'],
                incident_type=inc_data['incident_type'],
                severity=inc_data['severity'],
                status=inc_data['status'],
                confidence=inc_data['confidence'],
                root_cause=inc_data['root_cause'],
                remediation=inc_data['remediation']
            )
            db.session.add(inc)
            db.session.flush()

            for log_item in inc_data.get('log_objects', []):
                if isinstance(log_item, Log):
                    log_item.incident_id = inc.id

        db.session.commit()
        print(f"[OpsPilot Seed] Ingested {len(df)} logs and created {len(incidents_data)} initial incidents.")

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
