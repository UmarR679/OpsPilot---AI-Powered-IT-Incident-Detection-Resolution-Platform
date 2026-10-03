"""
Full verification script for OpsPilot Gemini migration.
Run from the OpsPilot root directory:
  python verify.py
"""
import requests

BASE = "http://localhost:5000"

def check(label, actual, expected, partial=True):
    ok = (expected in str(actual)) if partial else (actual == expected)
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {label}")
    if not ok:
        print(f"       Expected: {expected}")
        print(f"       Got:      {actual}")
    return ok

print("=" * 60)
print("OpsPilot Gemini Migration — Verification Suite")
print("=" * 60)

all_pass = True

# 1. Health endpoint
h = requests.get(f"{BASE}/api/health").json()
all_pass &= check("Health status is ok", h.get("status"), "ok")
all_pass &= check("Health contains gemini_configured field", "gemini_configured" in h, True, partial=False)
all_pass &= check("Health contains watsonx_configured (backward compat)", "watsonx_configured" in h, True, partial=False)
print(f"       gemini_configured = {h.get('gemini_configured')}")

# 2. Dashboard
d = requests.get(f"{BASE}/api/dashboard").json()
metrics = d.get("metrics", {})
all_pass &= check("Dashboard total_logs == 24", metrics.get("total_logs"), 24, partial=False)
all_pass &= check("Dashboard total_incidents == 9", metrics.get("total_incidents"), 9, partial=False)
all_pass &= check("Dashboard anomalous_logs > 0", metrics.get("anomalous_logs", 0) > 0, True, partial=False)

# 3. Incidents
incs = requests.get(f"{BASE}/api/incidents").json()
all_pass &= check("9 incidents seeded from sample CSV", len(incs), 9, partial=False)

# 4. Log-to-incident linking for incident with most logs
inc_with_logs = max(incs, key=lambda i: i["id"])
iid = None
for inc in incs:
    detail_check = requests.get(f"{BASE}/api/incidents/{inc['id']}").json()
    if len(detail_check.get("related_logs", [])) > 0:
        iid = inc["id"]
        detail = detail_check
        break

all_pass &= check("At least one incident has linked logs", iid is not None, True, partial=False)
if iid:
    print(f"       Incident #{iid} has {len(detail.get('related_logs', []))} linked logs")
    first_log = detail["related_logs"][0]
    all_pass &= check("Linked log has incident_id FK pointing to incident", first_log.get("incident_id"), iid, partial=False)

# 5. Analyze endpoint — test fallback
analyze_res = requests.post(f"{BASE}/api/incidents/{incs[0]['id']}/analyze").json()
all_pass &= check("Analyze endpoint returns ai_source field", "ai_source" in analyze_res, True, partial=False)
all_pass &= check("Analyze ai_source is 'fallback' (no API key)", analyze_res.get("ai_source"), "fallback", partial=False)
all_pass &= check("Fallback summary says 'Gemini' not 'Watsonx'", "Gemini" in analyze_res.get("ai_summary", ""), True, partial=False)
all_pass &= check("Fallback summary does NOT say 'Watsonx AI Unavailable'", "Watsonx AI Unavailable" not in analyze_res.get("ai_summary", ""), True, partial=False)
all_pass &= check("Analyze endpoint returns ai_summary field", analyze_res.get("ai_summary"), "Gemini")
all_pass &= check("Analyze endpoint returns remediation field", analyze_res.get("remediation"), "Simulated")
all_pass &= check("Analyze endpoint returns root_cause", analyze_res.get("root_cause") is not None, True, partial=False)

# 6. Resolve still works
resolve_res = requests.post(f"{BASE}/api/incidents/{incs[1]['id']}/resolve").json()
all_pass &= check("Resolve endpoint returns success message", resolve_res.get("message"), "resolved successfully")
all_pass &= check("Resolve endpoint creates resolution record", resolve_res.get("resolution") is not None, True, partial=False)

# 7. Resolutions history
ress = requests.get(f"{BASE}/api/resolutions").json()
all_pass &= check("Resolutions history is populated", len(ress) >= 1, True, partial=False)

print()
print("=" * 60)
print("RESULT:", "ALL TESTS PASSED [OK]" if all_pass else "SOME TESTS FAILED [FAIL]")
print("=" * 60)
