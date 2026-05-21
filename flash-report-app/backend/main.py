import csv
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CSV_PATH = Path("/workspace/manual_input.csv")
CSV_COLUMNS = ["Site", "Week", "Success_Story", "Tip", "Submitted_By", "Timestamp"]

SITES = [
    "BSB1", "CNF1", "FOR2", "GIG1", "GRU5", "GRU6", "GRU8", "GRU9",
    "POA1", "REC1", "REC3", "CGH3", "CGH7", "CNF7", "GIG7", "REC9",
    "DAM1", "DBH5", "DBR9", "DBS5", "DBZ1", "DCE3", "DCE5", "DES2",
    "DFR2", "DGO2", "DMG2", "DPB3", "DPE4", "DPR2", "DRJ3", "DRJ5",
    "DRS5", "DSA8", "DSP2", "DSP3", "DSP4", "DSP5", "ECB8", "EGO8",
    "ELP8", "EMG8", "EPE8", "EQU8", "ERS8", "ESA8", "ESB8", "ESE8",
    "ESS8", "EUA8", "EVT8", "VBJ1", "VBM1", "VBM2",
]


def get_current_week() -> str:
    today = datetime.now()
    # ISO week: YYYY-WXX
    year, week, _ = today.isocalendar()
    return f"{year}-W{week:02d}"


def get_user_from_midway(request: Request) -> str:
    # Try to get user from Midway headers injected by the proxy
    for header in ("x-forwarded-user", "x-amzn-oidc-identity", "x-midway-user", "x-user"):
        value = request.headers.get(header)
        if value:
            return value
    # Fall back to running `mcscli whoami` in the shell
    try:
        result = subprocess.run(
            ["mcscli", "whoami"], capture_output=True, text=True, timeout=5
        )
        user = result.stdout.strip()
        if user:
            return user
    except Exception:
        pass
    return "unknown"


def ensure_csv():
    if not CSV_PATH.exists():
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()


class SubmitInput(BaseModel):
    site: str
    week: str
    success_story: str
    tip: str


@app.get("/api/sites")
def list_sites():
    return {"sites": SITES}


@app.get("/api/week")
def current_week():
    return {"week": get_current_week()}


@app.post("/api/submit")
def submit(data: SubmitInput, request: Request):
    if data.site not in SITES:
        raise HTTPException(status_code=400, detail="Invalid site")
    if not data.week:
        raise HTTPException(status_code=400, detail="Week is required")

    ensure_csv()
    user = get_user_from_midway(request)
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    row = {
        "Site": data.site,
        "Week": data.week,
        "Success_Story": data.success_story,
        "Tip": data.tip,
        "Submitted_By": user,
        "Timestamp": timestamp,
    }

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writerow(row)

    return {"status": "ok", "submitted_by": user, "timestamp": timestamp}


@app.get("/api/entries")
def get_entries(week: str | None = None):
    ensure_csv()
    target_week = week or get_current_week()
    entries = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Week") == target_week:
                entries.append(row)
    return {"week": target_week, "entries": entries}


@app.get("/api/weeks")
def list_weeks():
    ensure_csv()
    weeks = set()
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            w = row.get("Week")
            if w:
                weeks.add(w)
    return {"weeks": sorted(weeks, reverse=True)}


ASSETS_DIR = Path("/workspace/assets")
ASSETS_DIR.mkdir(exist_ok=True)

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/svg+xml", "image/webp"}


@app.post("/api/upload/logo")
async def upload_logo(file: UploadFile = File(...), slot: str = Form("header-logo")):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Only PNG, JPG, SVG or WEBP allowed")
    allowed_slots = {
        "header-logo", "safetogo-logo", "amazon-logo", "card-brazil-bg", "card-others-bg",
        "icon-did-you-know", "icon-success-stories", "icon-hot-flag", "icon-best-dragonfly"
    }
    if slot not in allowed_slots:
        slot = "header-logo"
    # Icons go in assets/icons/
    if slot.startswith("icon-"):
        dest_dir = ASSETS_DIR / "icons"
        dest_dir.mkdir(exist_ok=True)
        suffix = Path(file.filename).suffix or ".png"
        dest = dest_dir / f"{slot}{suffix}"
        for old in dest_dir.glob(f"{slot}.*"):
            old.unlink()
    else:
        suffix = Path(file.filename).suffix or ".png"
        dest = ASSETS_DIR / f"{slot}{suffix}"
    else:
        for old in ASSETS_DIR.glob(f"{slot}.*"):
            old.unlink()
    content = await file.read()
    with open(dest, "wb") as f:
        f.write(content)
    return {"status": "ok", "path": str(dest), "filename": dest.name}


@app.get("/assets/{filename}")
def serve_asset(filename: str):
    path = ASSETS_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Asset not found")
    return FileResponse(path)


@app.get("/download/{filename}")
def download_file(filename: str):
    allowed = {"flash_report.py", "manual_input.csv", "flash_report_sample.csv", "flash-report.html", "upload.html"}
    if filename not in allowed:
        raise HTTPException(status_code=404, detail="File not found")
    paths = {
        "flash_report.py":       (Path("/workspace/flash_report.py"),       "application/octet-stream", True),
        "manual_input.csv":      (CSV_PATH,                                   "text/csv",                 True),
        "flash_report_sample.csv":(Path("/workspace/flash_report_sample.csv"),"text/csv",                 True),
        "flash-report.html":     (Path("/workspace/flash-report.html"),       "text/html",                False),
        "upload.html":           (Path("/workspace/upload.html"),             "text/html",                False),
    }
    if filename not in paths:
        raise HTTPException(status_code=404, detail="File not found")
    path, media, as_attachment = paths[filename]
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    headers = {}
    if as_attachment:
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return FileResponse(path, media_type=media, headers=headers)
