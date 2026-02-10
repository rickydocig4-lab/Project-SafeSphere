"""
SafeSphere Backend API (Supabase-ready placeholder)

This lightweight API accepts threat incident reports from the threat_cv engine
and stores each incident as a JSON file under `safesphere_backend/pending_incidents/`.

Backend team: replace the file-storage hooks with Supabase (or other DB) writes.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import json
import os


# ----- Config -----
DATA_DIR = Path("safesphere_backend")
PENDING_DIR = DATA_DIR / "pending_incidents"
SCREENSHOT_DIR = DATA_DIR / "screenshots"
PENDING_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


# ----- Models -----
class ThreatIncident(BaseModel):
    incident_id: str
    timestamp: str
    threat_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    threat_score: float
    people_count: int
    weapon_detected: bool
    weapon_types: List[str] = []
    behavior_summary: str
    is_critical: bool
    full_telemetry: Dict


class IncidentResponse(BaseModel):
    success: bool
    incident_id: str
    message: str


# ----- App -----
app = FastAPI(
    title="SafeSphere Threat Management API (Supabase-ready)",
    version="1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----- Helper: File storage (for backend team) -----
def save_incident_file(incident: Dict) -> bool:
    """Save incident JSON to pending folder for backend ingestion.
    Backend team can replace this with direct Supabase writes.
    """
    try:
        incident_id = incident.get("incident_id") or f"INC_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        path = PENDING_DIR / f"{incident_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(incident, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Failed to save incident file: {e}")
        return False


# ----- API Endpoints (simple contract for backend team) -----
@app.post("/threats/report", response_model=IncidentResponse)
async def report_threat(incident: ThreatIncident):
    """
    Receive a threat incident from the threat_cv engine.

    NOTE FOR BACKEND DEV: Replace `save_incident_file` internals with Supabase
    insert logic (or call Supabase HTTP REST endpoint). Keep the endpoint
    contract identical so the engine can POST directly.
    """
    data = incident.dict()
    print(f"Received threat report: {data.get('incident_id')}")

    # Save JSON file for backend ingestion (placeholder)
    saved = save_incident_file(data)
    if not saved:
        raise HTTPException(status_code=500, detail="Failed to persist incident")

    # Response: backend team will implement further actions (dispatch, alerts)
    return IncidentResponse(success=True, incident_id=data.get("incident_id"), message="Incident received and saved")


@app.get("/incidents")
async def list_incidents(limit: int = 100):
    """List recent pending incident files (for backend ingestion)."""
    files = sorted(PENDING_DIR.glob("*.json"), key=os.path.getmtime, reverse=True)[:limit]
    items = []
    for p in files:
        try:
            with open(p, "r", encoding="utf-8") as f:
                items.append(json.load(f))
        except Exception:
            continue
    return {"count": len(items), "incidents": items}


@app.get("/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Return saved incident JSON (placeholder storage)."""
    path = PENDING_DIR / f"{incident_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Incident not found")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.post("/upload/screenshot")
async def upload_screenshot(incident_id: str = Form(...), file: UploadFile = File(...)):
    """Upload screenshot associated with an incident. Backend can move to Supabase storage."""
    try:
        filename = f"{incident_id}_{file.filename}"
        filepath = SCREENSHOT_DIR / filename
        contents = await file.read()
        with open(filepath, "wb") as f:
            f.write(contents)
        return {"success": True, "incident_id": incident_id, "path": str(filepath)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "service": "SafeSphere Backend API"}


# ----- Notes for Backend Team -----
# - Replace `save_incident_file` with Supabase client code to insert into a table.
# - Recommended Supabase table columns:
#   incident_id, timestamp, threat_level, threat_score, people_count,
#   weapon_detected, weapon_types (JSON), behavior_summary, is_critical, full_telemetry (JSON), created_at
# - For screenshots/videos: either upload to Supabase storage bucket or provide endpoints to receive files and then store.


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
