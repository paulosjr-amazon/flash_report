#!/usr/bin/env python3
from pathlib import Path
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import anthropic
import uvicorn

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

ASSETS_DIR = Path("/home/paulosjr/.workspace/flash_report/assets")
ICONS_DIR = ASSETS_DIR / "icons"
ICONS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = {"image/png", "image/jpeg", "image/svg+xml", "image/webp", "text/csv", "application/csv", "application/vnd.ms-excel", "text/plain"}

SLOTS = {
    "header-logo":          ("assets", "🛡️ Logo Header (esq.)"),
    "safetogo-logo":        ("assets", "✅ Safe to Go"),
    "amazon-logo":          ("assets", "📦 Amazon"),
    "footer-logo":          ("assets", "🦶 Logo Rodapé"),
    "icon-did-you-know":    ("icons",  "💡 Did You Know?"),
    "icon-success-stories": ("icons",  "🏆 Success Stories"),
    "icon-hot-flag":        ("icons",  "🚩 Hot Flag"),
    "icon-best-dragonfly":  ("icons",  "🐉 Best Dragonfly"),
    "data-flash-report":    ("data",   "📊 Flash Report CSV"),
    "data-incidents":       ("data",   "🚨 Incidents CSV"),
    "data-nearmiss":        ("data",   "⚠️ Near Miss CSV"),
    "data-dragonfly":       ("data",   "🐉 Dragonfly CSV"),
    "data-inspections":     ("data",   "🔍 Inspections CSV"),
}

HTML = """<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Admin — Flash Report</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Inter',system-ui,sans-serif;background:#f2f2f2;min-height:100vh;display:flex;padding:0}
  .layout{display:grid;grid-template-columns:1fr 360px;width:100%;min-height:100vh}
  .panel-left{padding:2.5rem;display:flex;align-items:center;justify-content:center}
  .panel-right{background:#fff;border-left:1px solid #e8e8e8;padding:2rem 1.5rem;overflow-y:auto}
  .card{background:#fff;border-radius:20px;box-shadow:0 2px 20px rgba(0,0,0,.07);padding:2rem 2.25rem;width:100%;max-width:460px}
  h2{font-size:1rem;font-weight:800;color:#1a1a1a;margin-bottom:.2rem}
  .sub{font-size:.75rem;color:#888;margin-bottom:1.25rem}
  .section-label{font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#aaa;margin-bottom:.5rem;margin-top:1rem}
  .slots{display:grid;grid-template-columns:1fr 1fr;gap:.4rem;margin-bottom:.25rem}
  .slot{padding:.5rem .7rem;border:1.5px solid #e0e0e0;border-radius:10px;cursor:pointer;font-size:.72rem;font-weight:600;color:#555;background:#fafafa;transition:.15s}
  .slot:hover{border-color:#1c6b3a;background:#f4faf0}
  .slot.active{border-color:#1c6b3a;background:linear-gradient(90deg,#A8D872,#B7DCCB);color:#1c3d12}
  .drop{border:2px dashed #d4e8d5;border-radius:12px;padding:1.25rem;text-align:center;cursor:pointer;margin:.75rem 0;transition:.15s}
  .drop:hover{background:#f4faf0}
  .drop input{display:none}
  .drop-label{font-size:.82rem;color:#4CAF50;font-weight:600}
  .drop-hint{font-size:.68rem;color:#aaa;margin-top:.2rem}
  img#preview{display:none;max-height:60px;max-width:180px;margin:.5rem auto;border-radius:8px}
  .btn{width:100%;padding:.55rem;background:#1c6b3a;color:#fff;border:none;border-radius:999px;font-weight:700;font-size:.82rem;cursor:pointer}
  .btn:disabled{opacity:.4;cursor:not-allowed}
  .btn-dark{background:#3a3a3a}
  .msg{margin-top:.6rem;padding:.5rem .8rem;border-radius:8px;font-size:.75rem;display:none}
  .msg.ok{display:block;background:#edf5ee;color:#1c6b3a}
  .msg.err{display:block;background:#fde8e8;color:#c62828}
  .hist-title{font-size:.75rem;font-weight:800;color:#1a1a1a;margin-bottom:.75rem;display:flex;align-items:center;gap:.5rem}
  .hist-title span{background:#3a3a3a;color:#fff;font-size:.55rem;padding:.15rem .5rem;border-radius:999px}
  .hist-table{width:100%;border-collapse:collapse;font-size:.7rem}
  .hist-table th{padding:.4rem .5rem;text-align:left;font-weight:700;background:#f8f8f8;color:#555;border-bottom:1px solid #eee}
  .hist-table td{padding:.35rem .5rem;border-bottom:1px solid #f5f5f5}
  .st-pub{color:#2e7d32;font-weight:700;font-size:.62rem}
  .st-draft{color:#f57f17;font-weight:700;font-size:.62rem}
  .st-pend{color:#9e9e9e;font-weight:700;font-size:.62rem}
  .empty{text-align:center;color:#ccc;padding:2rem;font-size:.8rem}
</style>
</head>
<body>
<div class="layout">
  <div class="panel-left">
    <div class="card">
      <h2>⚙️ Admin — Flash Report</h2>
      <p class="sub">Upload de dados e recálculo do report</p>

      <div class="section-label">Logos</div>
      <div class="slots">
        <div class="slot active" data-slot="header-logo" onclick="setSlot(this)">🛡️ Header</div>
        <div class="slot" data-slot="safetogo-logo" onclick="setSlot(this)">✅ Safe to Go</div>
        <div class="slot" data-slot="amazon-logo" onclick="setSlot(this)">📦 Amazon</div>
        <div class="slot" data-slot="footer-logo" onclick="setSlot(this)">🦶 Rodapé</div>
      </div>

      <div class="section-label">Ícones</div>
      <div class="slots">
        <div class="slot" data-slot="icon-did-you-know" onclick="setSlot(this)">💡 Did You Know?</div>
        <div class="slot" data-slot="icon-success-stories" onclick="setSlot(this)">🏆 Success Stories</div>
        <div class="slot" data-slot="icon-hot-flag" onclick="setSlot(this)">🚩 Hot Flag</div>
        <div class="slot" data-slot="icon-best-dragonfly" onclick="setSlot(this)">🐉 Dragonfly</div>
      </div>

      <div class="section-label">Dados (CSV)</div>
      <div class="slots">
        <div class="slot" data-slot="data-flash-report" onclick="setSlot(this)">📊 Flash Report</div>
        <div class="slot" data-slot="data-incidents" onclick="setSlot(this)">🚨 Incidents</div>
        <div class="slot" data-slot="data-nearmiss" onclick="setSlot(this)">⚠️ Near Miss</div>
        <div class="slot" data-slot="data-dragonfly" onclick="setSlot(this)">🐉 Dragonfly</div>
        <div class="slot" data-slot="data-inspections" onclick="setSlot(this)">🔍 Inspections</div>
      </div>

      <div class="drop" onclick="document.getElementById('f').click()">
        <input type="file" id="f" accept=".png,.jpg,.jpeg,.svg,.webp,.csv" onchange="onFile(this)">
        <div class="drop-label">Clique para selecionar</div>
        <div class="drop-hint">PNG · JPG · SVG · WEBP · CSV</div>
      </div>
      <img id="preview" alt="preview">
      <button class="btn" id="btn" onclick="upload()" disabled>Fazer Upload</button>
      <div class="msg" id="msg"></div>

      <div style="margin-top:1.25rem;padding-top:1rem;border-top:1px solid #eee">
        <button class="btn btn-dark" onclick="recalc()">🔄 Recalcular e Abrir Flash Report</button>
        <div class="msg" id="msg2"></div>
      </div>
    </div>
  </div>

  <div class="panel-right">
    <div class="hist-title">Histórico de Emissões <span id="hist-count">0</span></div>
    <div id="history"></div>
  </div>
</div>

<script>
let slot = 'header-logo';
function setSlot(el){
  document.querySelectorAll('.slot').forEach(s=>s.classList.remove('active'));
  el.classList.add('active');
  slot = el.dataset.slot;
}
function onFile(input){
  const file = input.files[0];
  if(!file) return;
  document.getElementById('btn').disabled = false;
  if(file.type !== 'image/svg+xml'){
    const r = new FileReader();
    r.onload = e => { const img=document.getElementById('preview'); img.src=e.target.result; img.style.display='block'; };
    r.readAsDataURL(file);
  }
}
async function loadHistory(){
  const div = document.getElementById('history');
  const count = document.getElementById('hist-count');
  try{
    const res = await fetch('/api/report/history');
    const data = await res.json();
    count.textContent = data.entries.length;
    if(!data.entries.length){ div.innerHTML='<div class="empty">Nenhuma emissão registrada</div>'; return; }
    let html = '<table class="hist-table"><tr><th>Week</th><th>BU</th><th>Status</th><th>By</th><th>Date</th></tr>';
    data.entries.forEach(e => {
      const cls = e.status==='published'?'st-pub':e.status==='draft'?'st-draft':'st-pend';
      const ts = e.timestamp ? new Date(e.timestamp).toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'}) + ' ' + new Date(e.timestamp).toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'}) : '—';
      html += '<tr><td>'+e.week+'</td><td style="font-weight:600">'+e.bu+'</td><td><span class="'+cls+'">'+e.status.toUpperCase()+'</span></td><td>'+(e.submitted_by||'—')+'</td><td style="color:#999">'+ts+'</td></tr>';
    });
    html += '</table>';
    div.innerHTML = html;
  } catch(e){ div.innerHTML='<div class="empty" style="color:#c62828">Erro ao carregar</div>'; }
}
loadHistory();
async function recalc(){
  const msg = document.getElementById('msg2');
  msg.className='msg'; msg.style.display='none';
  try{
    const res = await fetch('/api/recalc', {method:'POST'});
    const data = await res.json();
    if(res.ok){
      msg.className='msg ok'; msg.textContent='✓ Atualizado! Redirecionando...';
      setTimeout(()=>{ window.location.href='https://ds-akyj2d5n--3000.us-east-1.prod.proxy.devspaces.amazon.dev/flash-report.html?mode=edit'; }, 1500);
    } else { msg.className='msg err'; msg.textContent='Erro: '+(data.detail||'falha'); }
  } catch(e){ msg.className='msg err'; msg.textContent='Erro de rede.'; }
}
async function upload(){
  const file = document.getElementById('f').files[0];
  if(!file) return;
  const btn=document.getElementById('btn'), msg=document.getElementById('msg');
  btn.disabled=true; btn.textContent='Enviando...'; msg.className='msg';
  const form = new FormData();
  form.append('file', file);
  form.append('slot', slot);
  try{
    const res = await fetch('/upload', {method:'POST', body:form});
    const data = await res.json();
    if(res.ok){ msg.className='msg ok'; msg.textContent='✓ Enviado: ' + data.filename; }
    else { msg.className='msg err'; msg.textContent='Erro: '+(data.detail||'falha'); }
  } catch(e){ msg.className='msg err'; msg.textContent='Erro de rede.'; }
  btn.disabled=false; btn.textContent='Fazer Upload';
}
</script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML

@app.post("/upload")
async def upload(file: UploadFile = File(...), slot: str = Form("header-logo")):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Tipo não permitido. Use PNG, JPG, SVG ou WEBP.")
    if slot not in SLOTS:
        raise HTTPException(400, "Slot inválido.")
    data_dir = ASSETS_DIR.parent / "data"
    data_dir.mkdir(exist_ok=True)
    dest_dir = ICONS_DIR if SLOTS[slot][0] == "icons" else (data_dir if SLOTS[slot][0] == "data" else ASSETS_DIR)
    suffix = Path(file.filename).suffix or ".png"
    for old in dest_dir.glob(f"{slot}.*"):
        old.unlink()
    dest = dest_dir / f"{slot}{suffix}"
    dest.write_bytes(await file.read())
    return {"status": "ok", "filename": dest.name}

app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")


# ── Report State ──────────────────────────────────────────────────────────────

REPORT_STATE_FILE = ASSETS_DIR.parent / "report_states.json"
BUS = ["BR", "FC", "SC", "LOG"]
BU_LABELS = {"BR": "Brazil Operations", "FC": "Fulfillment Centers", "SC": "Sort Centers", "LOG": "Logistics"}

def load_states() -> dict:
    if REPORT_STATE_FILE.exists():
        import json
        return json.loads(REPORT_STATE_FILE.read_text())
    return {}

def save_states(data: dict):
    import json
    REPORT_STATE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))

class ReportSaveRequest(BaseModel):
    week: str
    bu: str
    status: str   # "draft" | "published"
    content: dict
    submitted_by: str = "anonymous"

@app.get("/api/report/status")
def get_report_status(week: str):
    states = load_states()
    week_data = states.get(week, {})
    result = []
    for bu in BUS:
        entry = week_data.get(bu, {})
        result.append({
            "bu": bu,
            "label": BU_LABELS[bu],
            "status": entry.get("status", "pending"),
            "submitted_by": entry.get("submitted_by"),
            "timestamp": entry.get("timestamp"),
        })
    return {"week": week, "bus": result}

@app.get("/api/report/content")
def get_report_content(week: str, bu: str):
    states = load_states()
    entry = states.get(week, {}).get(bu, {})
    return {"week": week, "bu": bu, "content": entry.get("content", {})}

@app.post("/api/report/save")
def save_report(req: ReportSaveRequest):
    import json
    from datetime import datetime, timezone
    states = load_states()
    if req.week not in states:
        states[req.week] = {}
    states[req.week][req.bu] = {
        "status": req.status,
        "content": req.content,
        "submitted_by": req.submitted_by,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    save_states(states)
    return {"ok": True, "status": req.status}

@app.get("/api/report/history")
def get_report_history():
    states = load_states()
    entries = []
    for week, bus in sorted(states.items(), reverse=True):
        for bu, data in sorted(bus.items()):
            entries.append({
                "week": week,
                "bu": BU_LABELS.get(bu, bu),
                "status": data.get("status", "pending"),
                "submitted_by": data.get("submitted_by"),
                "timestamp": data.get("timestamp"),
            })
    return {"entries": entries}

@app.get("/api/weeks")
def get_weeks():
    states = load_states()
    return {"weeks": sorted(states.keys(), reverse=True)}


# ── Recalculate Flash Report ──────────────────────────────────────────────────

@app.post("/api/recalc")
def recalculate_report():
    import csv, re
    from collections import defaultdict
    from datetime import datetime as dt

    DATA_DIR = ASSETS_DIR.parent / "data"
    FLASH_CSV = DATA_DIR / "data-flash-report.csv"
    HTML_FILE = ASSETS_DIR.parent / "flash-report.html"
    PUBLIC_FILE = Path("/home/paulosjr/.workspace/flash-report/public/flash-report.html")

    if not FLASH_CSV.exists():
        raise HTTPException(400, "data-flash-report.csv not found. Upload it first.")
    if not HTML_FILE.exists():
        raise HTTPException(400, "flash-report.html not found.")

    rows = list(csv.DictReader(open(FLASH_CSV, encoding='utf-8-sig')))

    # Detect latest week
    weeks = sorted(set(r['Week'] for r in rows if r.get('Week','')))
    if not weeks:
        raise HTTPException(400, "No week data found in CSV.")
    latest_week = weeks[-1]
    week_rows = [r for r in rows if r['Week'] == latest_week]

    def sf(v):
        try: return float(str(v).strip().replace(',','.')) if v and str(v).strip() else 0.0
        except: return 0.0

    def rate(n, h): return (n * 200000 / h) if h > 0 else 0
    def pct(n, d): return (n / d * 100) if d > 0 else 0
    def fmt(v, d=2): return f'{v:.{d}f}'
    def fmt_pct(v): return f'{v:.1f}%'

    def calc_bu(bu_rows, all_rows):
        h_w = sum(sf(r['Total_Hours_Week']) for r in bu_rows)
        h_y = sum(sf(r['Total_Hours_YTD']) for r in all_rows)
        si_w = sum(sf(r['INC_SI_Week']) for r in bu_rows)
        si_y = sum(sf(r['INC_SI_YTD']) for r in all_rows)
        ri_w = sum(sf(r['INC_RI_Week']) for r in bu_rows)
        ri_y = sum(sf(r['INC_RI_YTD']) for r in all_rows)
        lti_w = sum(sf(r['INC_LTI_Week']) for r in bu_rows)
        lti_y = sum(sf(r['INC_LTI_YTD']) for r in all_rows)
        fai_w = sum(sf(r['INC_FAI_Week']) for r in bu_rows)
        fai_y = sum(sf(r['INC_FAI_YTD']) for r in all_rows)
        nm_w = sum(sf(r['INC_Near_Miss_Week']) for r in bu_rows)
        nm_y = sum(sf(r['INC_Near_Miss_YTD']) for r in all_rows)
        dfy_obs_w = sum(sf(r['DFY_Total_Obs_Week']) for r in bu_rows)
        dfy_obs_y = sum(sf(r['DFY_Total_Obs_YTD']) for r in all_rows)
        dfy_closed_w = sum(sf(r['DFY_Closed_Week']) for r in bu_rows)
        dfy_closed_y = sum(sf(r['DFY_Closed_YTD']) for r in all_rows)
        insp_ontime_w = sum(sf(r['INSP_On_Time_Week']) for r in bu_rows)
        insp_ontime_y = sum(sf(r['INSP_On_Time_YTD']) for r in all_rows)
        insp_due_w = sum(sf(r['INSP_Due_Insp_Week']) for r in bu_rows)
        insp_due_y = sum(sf(r['INSP_Due_Insp_YTD']) for r in all_rows)
        return {
            'sir': (fmt(rate(si_w,h_w)), fmt(rate(si_y,h_y))),
            'rir': (fmt(rate(ri_w,h_w)), fmt(rate(ri_y,h_y))),
            'ltir': (fmt(rate(lti_w,h_w)), fmt(rate(lti_y,h_y))),
            'fair': (fmt(rate(fai_w,h_w)), fmt(rate(fai_y,h_y))),
            'dfy_rate': (fmt(rate(dfy_obs_w,h_w),1), fmt(rate(dfy_obs_y,h_y),1)),
            'dfy_closure': (fmt_pct(pct(dfy_closed_w,dfy_obs_w)), fmt_pct(pct(dfy_closed_y,dfy_obs_y))),
            'insp_otc': (fmt_pct(pct(insp_ontime_w,insp_due_w)), fmt_pct(pct(insp_ontime_y,insp_due_y))),
            'nm': (fmt(rate(nm_w,h_w),1), fmt(rate(nm_y,h_y),1)),
        }

    fc_w = [r for r in week_rows if r['BU']=='LATAMCF']
    sc_w = [r for r in week_rows if r['BU']=='ATS-LATAM']
    log_w = [r for r in week_rows if r['BU']=='AMZL-LATAM']
    fc_all = [r for r in rows if r['BU']=='LATAMCF']
    sc_all = [r for r in rows if r['BU']=='ATS-LATAM']
    log_all = [r for r in rows if r['BU']=='AMZL-LATAM']

    agg = {
        'Brazil': calc_bu(week_rows, rows),
        'FC': calc_bu(fc_w, fc_all),
        'SC': calc_bu(sc_w, sc_all),
        'Logistics': calc_bu(log_w, log_all),
    }

    # Patch HTML
    html = HTML_FILE.read_text(encoding='utf-8')

    COL_ORDER = ['Brazil', 'FC', 'SC', 'Logistics']
    EVENTS_METRICS = ['sir', 'rir', 'ltir', 'fair']
    BARRIERS_METRICS = ['dfy_rate', 'dfy_closure', 'insp_otc', 'nm']

    wk_pattern = r'(<div class="metric-wk">)([^<]*)(<\/div>)'
    ytd_pattern = r'(<div class="metric-ytd-val">)([^<]*)(<\/div>)'

    def patch_section(html, pill_text, metrics):
        start = html.find(f'<span class="pill">{pill_text}</span>')
        if start == -1: return html
        end = html.find('<div style="height:3px', start)
        if end == -1: end = html.find('<div class="hl-grid"', start)
        if end == -1: return html
        chunk = html[start:end]
        wk_matches = list(re.finditer(wk_pattern, chunk))
        ytd_matches = list(re.finditer(ytd_pattern, chunk))
        vals = []
        for col in COL_ORDER:
            for metric in metrics:
                w, y = agg[col][metric]
                vals.append((w, y))
        replacements = []
        for i, (w, y) in enumerate(vals):
            if i < len(wk_matches):
                replacements.append((wk_matches[i].start(), wk_matches[i].end(), f'<div class="metric-wk">{w}</div>'))
            if i < len(ytd_matches):
                replacements.append((ytd_matches[i].start(), ytd_matches[i].end(), f'<div class="metric-ytd-val">{y}</div>'))
        replacements.sort(key=lambda x: x[0], reverse=True)
        for s, e, new in replacements:
            chunk = chunk[:s] + new + chunk[e:]
        return html[:start] + chunk + html[end:]

    html = patch_section(html, 'Events', EVENTS_METRICS)
    html = patch_section(html, 'Barriers', BARRIERS_METRICS)

    # Update week references
    html = re.sub(r'Week 2026-W\d+', f'Week 2026-W{latest_week}', html)

    HTML_FILE.write_text(html, encoding='utf-8')
    if PUBLIC_FILE.parent.exists():
        PUBLIC_FILE.write_text(html, encoding='utf-8')

    return {"ok": True, "detail": f"Week {latest_week} — {len(week_rows)} sites updated"}


# ── Claude AI Insights ────────────────────────────────────────────────────────

import os
CLAUDE_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

class InsightsRequest(BaseModel):
    bu: str          # "Brazil Operations" | "Fulfillment Centers" | "Sort Centers" | "Logistics"
    section: str     # "events" | "barriers"
    metrics: dict    # {metric_name: {week: val, ytd: val}, ...}

class SnapRequest(BaseModel):
    field: str
    prompt: str

@app.post("/api/snap")
async def generate_snap(req: SnapRequest):
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": req.prompt}]
    )
    return {"text": response.content[0].text.strip()}


@app.post("/api/insights")
async def generate_insights(req: InsightsRequest):
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    metrics_text = "\n".join(
        f"- {k}: Week={v.get('week','?')}  YTD={v.get('ytd','?')}"
        for k, v in req.metrics.items()
    )

    prompt = f"""You are a WHS (Workplace Health & Safety) analyst for Amazon Brazil Operations.

Business Unit: {req.bu}
Section: {req.section.upper()} metrics

Weekly data:
{metrics_text}

Generate exactly:
1. Three bullet points for HIGHLIGHTS (positive results, improvements, achievements)
2. Three bullet points for LOWLIGHTS (concerns, areas needing attention, below-target metrics)

Rules:
- Each bullet is one concise sentence (max 20 words)
- Reference specific metrics and numbers from the data
- Be objective and operational in tone
- No markdown, no asterisks, just plain text bullets starting with a dash

Format your response as:
HIGHLIGHTS:
- ...
- ...
- ...
LOWLIGHTS:
- ...
- ...
- ..."""

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text.strip()

    highlights, lowlights = [], []
    section = None
    for line in text.splitlines():
        line = line.strip()
        if line.upper().startswith("HIGHLIGHTS"):
            section = "h"
        elif line.upper().startswith("LOWLIGHTS"):
            section = "l"
        elif line.startswith("-") and section == "h":
            highlights.append(line[1:].strip())
        elif line.startswith("-") and section == "l":
            lowlights.append(line[1:].strip())

    return {"highlights": highlights, "lowlights": lowlights}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3003)
