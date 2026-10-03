import os
from google import genai
from config import Config

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY', Config.GEMINI_API_KEY)
        self.model_name = os.getenv('GEMINI_MODEL', Config.GEMINI_MODEL)
        self._client = None

    def is_configured(self):
        # Refresh API key from env/config if updated dynamically
        self.api_key = os.getenv('GEMINI_API_KEY', Config.GEMINI_API_KEY)
        return bool(self.api_key and self.api_key.strip())

    def _get_client(self):
        if not self.is_configured():
            return None
        if not self._client:
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[Gemini Client Init Error] {e}")
                return None
        return self._client

    def analyze_incident(self, incident_title, incident_type, severity, root_cause, evidence_logs=""):
        """
        Sends analysis prompt to Google Gemini API or returns rule-based local fallback response.
        """
        client = self._get_client()
        if not client:
            return self._generate_fallback(incident_title, incident_type, severity, root_cause, is_missing_config=True)

        prompt = f"""
You are an expert IT Operations & Reliability Engineer (SRE). Analyze the following system incident and provide a concise, structured response.

Incident Title: {incident_title}
Incident Type: {incident_type}
Severity: {severity}
Detected Root Cause: {root_cause}
Log Evidence: {evidence_logs}

Format your output into 4 clear sections:
1. INCIDENT SUMMARY: High-level executive overview of what occurred.
2. TECHNICAL EXPLANATION: In-depth technical breakdown of system components involved.
3. PROBABLE ROOT CAUSE: Precise root cause analysis.
4. RECOMMENDED REMEDIATION: Concrete, step-by-step remediation actions.
IMPORTANT OUTPUT FORMAT:

Return clean, professional plain text only.

AI Incident Summary:
Write one short, clear paragraph explaining what happened.

Technical Explanation:
Write 2 to 4 clear bullet points. Put each bullet on a separate line.

Recommended Remediation:
Write 3 to 5 numbered action points. Put each action on a separate line.

Formatting rules:
- Do not use Markdown.
- Do not use **bold** text.
- Do not use # headings.
- Do not use --- separators.
- Do not use code blocks.
- Keep the language simple and professional.
- Avoid repeating information.
- Only use information supported by the incident logs.
"""

        try:
            model_to_use = os.getenv('GEMINI_MODEL', self.model_name) or 'gemini-2.5-flash'
            response = client.models.generate_content(
                model=model_to_use,
                contents=prompt,
            )
            if response and response.text:
                parsed = self._parse_gemini_output(response.text, incident_type)
                parsed['ai_source'] = 'gemini'
                return parsed
        except Exception as e:
            print(f"[Gemini Generation Exception] Request failed: {e}")

        return self._generate_fallback(incident_title, incident_type, severity, root_cause, is_missing_config=False)

    def _parse_gemini_output(self, text, incident_type):
        lines = text.strip().split('\n')
        summary, explanation, root_cause, remediation = "", "", "", ""
        
        current_section = None
        for line in lines:
            line_str = line.strip()
            if "INCIDENT SUMMARY" in line_str.upper():
                current_section = "summary"
                continue
            elif "TECHNICAL EXPLANATION" in line_str.upper():
                current_section = "explanation"
                continue
            elif "PROBABLE ROOT CAUSE" in line_str.upper():
                current_section = "root_cause"
                continue
            elif "RECOMMENDED REMEDIATION" in line_str.upper():
                current_section = "remediation"
                continue

            if current_section == "summary":
                summary += " " + line_str
            elif current_section == "explanation":
                explanation += " " + line_str
            elif current_section == "root_cause":
                root_cause += " " + line_str
            elif current_section == "remediation":
                remediation += " " + line_str

        return {
            'ai_summary': summary.strip() or f"Google Gemini Summary: Critical {incident_type} anomaly detected.",
            'ai_explanation': explanation.strip() or text[:300],
            'probable_root_cause': root_cause.strip() or "Analyzed by Google Gemini model.",
            'remediation': remediation.strip() or "Apply recommended system patch and restart process."
        }

    def _generate_fallback(self, incident_title, incident_type, severity, root_cause, is_missing_config=True):
        status_note = "[Gemini unavailable — using local analysis]" if is_missing_config else "[Gemini API connection error — using local analysis]"
        
        summaries = {
            'CPU': f"{status_note} High CPU saturation detected on service compute cluster causing system response delays.",
            'Memory': f"{status_note} Memory leak and heap space depletion detected leading to process crashes.",
            'Disk': f"{status_note} Storage volume capacity threshold exceeded resulting in write-ahead log write failures.",
            'Network': f"{status_note} Gateway socket timeouts and packet drops causing connectivity interruptions.",
            'Database': f"{status_note} Relational database connection pool depletion and transaction lock contention.",
            'Application': f"{status_note} Unhandled application level runtime exceptions resulting in server error 500.",
            'Unknown': f"{status_note} General log anomaly detected requiring system administrator inspection."
        }

        explanations = {
            'CPU': f"{status_note} The compute worker experienced sustained CPU utilization over 95%, leading to thread pool saturation and API latency spikes.",
            'Memory': f"{status_note} JVM heap memory limit was exceeded (3.5GB / 4.0GB allocated), triggering an out-of-memory exception and kernel process termination.",
            'Disk': f"{status_note} Disk storage on volume /data/db reached 92% capacity, causing I/O queue latency spikes and failing transaction write-ahead log writes.",
            'Network': f"{status_note} Network interface eth0 recorded 5.2% packet drops and socket connection timeouts when reaching upstream dependencies.",
            'Database': f"{status_note} All available PostgreSQL database connections (82/100) were acquired, leading to query wait timeouts and row deadlocks.",
            'Application': f"{status_note} Application controller threw an unhandled NullPointerException while attempting to render payment response views.",
            'Unknown': f"{status_note} Log frequency and anomaly scoring algorithm detected unusual log patterns in system trace."
        }

        remediations = {
            'CPU': 'Simulated restart of affected service (CPU throttling & worker refresh)',
            'Memory': 'Simulated memory pool flush & worker restart',
            'Disk': 'Simulated log rotation & temporary cache purge',
            'Network': 'Simulated network service restart',
            'Database': 'Simulated database connection pool reset',
            'Application': 'Simulated application service restart',
            'Unknown': 'Simulated diagnostic service reboot'
        }

        return {
            'ai_summary': summaries.get(incident_type, summaries['Unknown']),
            'ai_explanation': explanations.get(incident_type, explanations['Unknown']),
            'probable_root_cause': f"{status_note} {root_cause}",
            'remediation': remediations.get(incident_type, remediations['Unknown']),
            'ai_source': 'fallback'
        }

gemini_service = GeminiService()
