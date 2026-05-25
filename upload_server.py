#!/usr/bin/env python3
import os
from pathlib import Path
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import anthropic
import uvicorn

CLAUDE_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

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
    "icon-best-dragonfly":  ("icons",  "📋 Best Dragonfly"),
    "data-flash-report":    ("data",   "📊 Flash Report CSV"),
    "data-incidents":       ("data",   "🚨 Incidents CSV"),
    "data-nearmiss":        ("data",   "⚠️ Near Miss CSV"),
    "data-dragonfly":       ("data",   "📋 Dragonfly CSV"),
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
  .layout{display:grid;grid-template-columns:1fr 400px;width:100%;min-height:100vh}
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
  /* Analytics Stats Section */
  .stats-section{margin-bottom:1.5rem;padding-bottom:1.25rem;border-bottom:1px solid #eee}
  .stats-header{display:flex;align-items:center;gap:.5rem;margin-bottom:.75rem}
  .stats-header h3{font-size:.75rem;font-weight:800;color:#1a1a1a;margin:0}
  .stats-header .badge{background:linear-gradient(135deg,#8FD44F,#A8D872);color:#1c3d12;font-size:.5rem;font-weight:800;padding:.15rem .5rem;border-radius:999px;text-transform:uppercase;letter-spacing:.05em}
  .stats-grid{display:grid;grid-template-columns:1fr 1fr;gap:.5rem}
  .stat-card{background:#f4faf0;border:1.5px solid #d4e8d5;border-radius:12px;padding:.6rem .7rem;transition:.15s}
  .stat-card:hover{border-color:#8FD44F;box-shadow:0 2px 8px rgba(143,212,79,.15)}
  .stat-card.warn{background:#fff8e1;border-color:#ffe082}
  .stat-card.alert{background:#fde8e8;border-color:#ef9a9a}
  .stat-val{font-size:1.1rem;font-weight:900;color:#1c6b3a;line-height:1.2}
  .stat-card.warn .stat-val{color:#f57f17}
  .stat-card.alert .stat-val{color:#c62828}
  .stat-lbl{font-size:.58rem;color:#777;font-weight:600;text-transform:uppercase;letter-spacing:.04em;margin-top:.15rem}
  .stat-sub{font-size:.55rem;color:#aaa;margin-top:.1rem}
  .stats-row{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:.4rem;margin-top:.5rem}
  .stat-mini{text-align:center;background:#fff;border:1px solid #eee;border-radius:8px;padding:.4rem .3rem}
  .stat-mini .stat-val{font-size:.85rem;color:#1c6b3a}
  .stat-mini .stat-lbl{font-size:.5rem;margin-top:.1rem}
  .stats-loading{text-align:center;padding:1rem;color:#aaa;font-size:.7rem}
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
        <div class="slot" data-slot="icon-best-dragonfly" onclick="setSlot(this)">📋 Dragonfly</div>
      </div>

      <div class="section-label">Dados (CSV)</div>
      <div class="slots">
        <div class="slot" data-slot="data-flash-report" onclick="setSlot(this)">📊 Flash Report</div>
        <div class="slot" data-slot="data-incidents" onclick="setSlot(this)">🚨 Incidents</div>
        <div class="slot" data-slot="data-nearmiss" onclick="setSlot(this)">⚠️ Near Miss</div>
        <div class="slot" data-slot="data-dragonfly" onclick="setSlot(this)">📋 Dragonfly</div>
        <div class="slot" data-slot="data-inspections" onclick="setSlot(this)">🔍 Inspections</div>
      </div>

      <div class="section-label" style="margin-top:1.25rem">Dataset Status</div>
      <div id="dataset-status" style="margin-bottom:.75rem;font-size:.7rem;color:#555"></div>

      <div class="drop" onclick="document.getElementById('f').click()">
        <input type="file" id="f" accept=".png,.jpg,.jpeg,.svg,.webp,.csv" onchange="onFile(this)">
        <div class="drop-label">Clique para selecionar</div>
        <div class="drop-hint">PNG · JPG · SVG · WEBP · CSV</div>
      </div>
      <img id="preview" alt="preview">
      <button class="btn" id="btn" onclick="upload()" disabled>Fazer Upload</button>
      <div class="msg" id="msg"></div>

      <div style="margin-top:1.25rem;padding-top:1rem;border-top:1px solid #eee">
        <div class="section-label">Large File Import (500MB+)</div>
        <div style="font-size:.62rem;color:#888;margin-bottom:.4rem">Place file in <code>~/shared/</code> then import:</div>
        <div style="display:flex;gap:.4rem;margin-bottom:.6rem">
          <input id="import-path" type="text" placeholder="~/shared/inspections.csv" style="flex:1;padding:.4rem .6rem;border:1.5px solid #e0e0e0;border-radius:8px;font-size:.72rem;outline:none">
          <select id="import-slot" style="padding:.4rem;border:1.5px solid #e0e0e0;border-radius:8px;font-size:.68rem">
            <option value="data-flash-report">Flash Report</option>
            <option value="data-incidents">Incidents</option>
            <option value="data-nearmiss">Near Miss</option>
            <option value="data-dragonfly">Dragonfly</option>
            <option value="data-inspections" selected>Inspections</option>
          </select>
        </div>
        <button class="btn" onclick="importFile()" style="background:#555">Import from Server</button>
        <div class="msg" id="msg3"></div>
      </div>

      <div style="margin-top:1.25rem;padding-top:1rem;border-top:1px solid #eee">
        <button class="btn btn-dark" onclick="recalc()">🔄 Recalcular e Abrir Flash Report</button>
        <div class="msg" id="msg2"></div>
      </div>
    </div>
  </div>

  <div class="panel-right">
    <div class="stats-section" id="stats-section">
      <div class="stats-header">
        <h3>Analytics Dashboard</h3>
        <span class="badge">Live</span>
      </div>
      <div id="stats-content"><div class="stats-loading">Loading stats...</div></div>
    </div>
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

async function loadDatasetStatus() {
  const div = document.getElementById('dataset-status');
  try {
    const res = await fetch('/api/datasets');
    const data = await res.json();
    div.innerHTML = data.datasets.map(d => {
      const ts = d.updated ? new Date(d.updated).toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit',year:'numeric'}) + ' ' + new Date(d.updated).toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'}) : '—';
      const color = d.exists ? '#2e7d32' : '#c62828';
      const icon = d.exists ? '✓' : '✗';
      return `<div style="display:flex;align-items:center;justify-content:space-between;padding:.35rem .5rem;border-bottom:1px solid #f0f0f0">
        <span><span style="color:${color};font-weight:800">${icon}</span> ${d.label}</span>
        <span style="color:#999;font-size:.62rem">${d.exists ? ts + ' · ' + d.size_kb + 'KB' : 'Not uploaded'}</span>
      </div>`;
    }).join('');
  } catch(e) { div.innerHTML = '<span style="color:#c62828">Error loading status</span>'; }
}
loadDatasetStatus();

async function loadAdminStats() {
  const container = document.getElementById('stats-content');
  try {
    const res = await fetch('/api/admin-stats');
    const d = await res.json();
    let html = '';

    // Report Status
    html += '<div style="margin-bottom:.6rem"><div style="font-size:.6rem;font-weight:700;color:#555;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.35rem">Report Status — W' + d.report_status.week + '</div>';
    html += '<div class="stats-grid">';
    html += '<div class="stat-card"><div class="stat-val">' + d.report_status.published + '</div><div class="stat-lbl">Published</div></div>';
    const pendClass = d.report_status.pending > 0 ? ' warn' : '';
    html += '<div class="stat-card' + pendClass + '"><div class="stat-val">' + d.report_status.pending + '/' + d.report_status.draft + '</div><div class="stat-lbl">Pending / Draft</div></div>';
    html += '</div></div>';

    // Dataset Health
    html += '<div style="margin-bottom:.6rem"><div style="font-size:.6rem;font-weight:700;color:#555;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.35rem">Dataset Health</div>';
    html += '<div class="stats-grid">';
    const hhtVal = d.dataset_health.total_hht > 1000000 ? (d.dataset_health.total_hht/1000000).toFixed(1)+'M' : d.dataset_health.total_hht > 1000 ? (d.dataset_health.total_hht/1000).toFixed(0)+'K' : d.dataset_health.total_hht.toFixed(0);
    html += '<div class="stat-card"><div class="stat-val">' + hhtVal + '</div><div class="stat-lbl">Total HHT (Week)</div><div class="stat-sub">' + d.dataset_health.sites_count + ' sites</div></div>';
    const missingClass = d.dataset_health.missing_sites > 0 ? ' alert' : '';
    html += '<div class="stat-card' + missingClass + '"><div class="stat-val">' + d.dataset_health.missing_sites + '</div><div class="stat-lbl">Missing Sites</div><div class="stat-sub">vs prev weeks</div></div>';
    html += '</div>';
    // Freshness
    html += '<div style="margin-top:.4rem;font-size:.55rem;color:#999">';
    d.dataset_health.freshness.forEach(f => {
      const icon = f.age_hours < 48 ? '🟢' : f.age_hours < 168 ? '🟡' : '🔴';
      html += '<div style="display:flex;justify-content:space-between;padding:.15rem 0">' + icon + ' ' + f.label + '<span>' + f.age_text + '</span></div>';
    });
    html += '</div></div>';

    // Key Metrics
    html += '<div><div style="font-size:.6rem;font-weight:700;color:#555;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.35rem">Key Metrics — Brazil W' + d.report_status.week + '</div>';
    html += '<div class="stats-row">';
    const metrics = d.key_metrics;
    html += '<div class="stat-mini"><div class="stat-val">' + metrics.sir + '</div><div class="stat-lbl">SIR</div></div>';
    html += '<div class="stat-mini"><div class="stat-val">' + metrics.rir + '</div><div class="stat-lbl">RIR</div></div>';
    html += '<div class="stat-mini"><div class="stat-val">' + metrics.ltir + '</div><div class="stat-lbl">LTIR</div></div>';
    html += '<div class="stat-mini"><div class="stat-val">' + metrics.fair + '</div><div class="stat-lbl">FAIR</div></div>';
    html += '</div>';
    html += '<div class="stats-row" style="margin-top:.35rem">';
    html += '<div class="stat-mini"><div class="stat-val">' + metrics.near_miss + '</div><div class="stat-lbl">Near Miss</div></div>';
    html += '<div class="stat-mini"><div class="stat-val">' + metrics.dfy_rate + '</div><div class="stat-lbl">DFY Rate</div></div>';
    html += '<div class="stat-mini"><div class="stat-val">' + metrics.insp_otc + '</div><div class="stat-lbl">Insp OTC</div></div>';
    html += '<div class="stat-mini"><div class="stat-val">' + metrics.total_incidents + '</div><div class="stat-lbl">All Inc.</div></div>';
    html += '</div></div>';

    container.innerHTML = html;
  } catch(e) { container.innerHTML = '<div class="stats-loading" style="color:#c62828">Failed to load stats</div>'; }
}
loadAdminStats();

async function recalc(){
  const msg = document.getElementById('msg2');
  msg.className='msg'; msg.style.display='none';
  try{
    const res = await fetch('/api/recalc', {method:'POST'});
    const data = await res.json();
    if(res.ok){
      let txt = '✓ W' + data.week + ' — ' + data.sites_count + ' sites updated';
      if (data.missing_count > 0) {
        txt += '\\n\\n⚠️ ' + data.missing_count + ' sites missing (need HHT):\\n' + data.missing_sites.join(', ');
      }
      msg.className='msg ok'; msg.style.whiteSpace='pre-line'; msg.textContent=txt;
      setTimeout(()=>{ window.location.href='https://ds-akyj2d5n--3000.us-east-1.prod.proxy.devspaces.amazon.dev/flash-report.html?mode=edit'; }, 4000);
    } else { msg.className='msg err'; msg.textContent='Error: '+(data.detail||'failed'); }
  } catch(e){ msg.className='msg err'; msg.textContent='Network error.'; }
}
async function upload(){
  const file = document.getElementById('f').files[0];
  if(!file) return;
  const btn=document.getElementById('btn'), msg=document.getElementById('msg');
  btn.disabled=true; msg.className='msg';

  const CHUNK_SIZE = 20 * 1024 * 1024; // 20MB chunks
  const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
  const uploadId = Date.now().toString(36);

  try {
    if (file.size <= CHUNK_SIZE) {
      // Small file: direct upload
      btn.textContent='Uploading...';
      const form = new FormData();
      form.append('file', file);
      form.append('slot', slot);
      const res = await fetch('/upload', {method:'POST', body:form});
      const data = await res.json();
      if(res.ok) { showReport(data, msg); loadDatasetStatus(); }
      else { msg.className='msg err'; msg.textContent='Error: '+(data.detail||'failed'); }
    } else {
      // Large file: chunked upload
      for (let i = 0; i < totalChunks; i++) {
        const start = i * CHUNK_SIZE;
        const end = Math.min(start + CHUNK_SIZE, file.size);
        const chunk = file.slice(start, end);
        const pct = Math.round((i+1)/totalChunks*100);
        btn.textContent = `Uploading... ${pct}%`;

        const form = new FormData();
        form.append('file', chunk, file.name);
        form.append('slot', slot);
        form.append('chunk_index', i);
        form.append('total_chunks', totalChunks);
        form.append('upload_id', uploadId);

        const res = await fetch('/upload-chunk', {method:'POST', body:form});
        if (!res.ok) { msg.className='msg err'; msg.textContent='Error at chunk '+(i+1); btn.disabled=false; btn.textContent='Fazer Upload'; return; }
        const data = await res.json();
        if (data.complete) { showReport(data, msg); loadDatasetStatus(); }
      }
    }
  } catch(e){ msg.className='msg err'; msg.textContent='Network error: '+e.message; }
  btn.disabled=false; btn.textContent='Fazer Upload';
}

function showReport(data, msg) {
  let txt = '✓ Uploaded: ' + data.filename;
  if(data.report) {
    const r = data.report;
    txt += '\\n' + r.total_rows + ' rows';
    if(r.weeks) {
      txt += '\\n';
      Object.entries(r.weeks).forEach(([w, d]) => {
        if (typeof d === 'object') { txt += w + ': ' + d.sites + ' sites (' + Object.entries(d.by_bu).map(([bu,n]) => bu+'='+n).join(', ') + ')\\n'; }
        else { txt += w + ': ' + d + ' sites\\n'; }
      });
    }
    if(r.by_bu) { txt += '\\nBy BU: ' + Object.entries(r.by_bu).map(([bu,n]) => bu+'='+n).join(', '); }
  }
  msg.className='msg ok'; msg.style.whiteSpace='pre-line'; msg.textContent=txt;
}

async function importFile() {
  const path = document.getElementById('import-path').value.trim();
  const slot = document.getElementById('import-slot').value;
  const msg = document.getElementById('msg3');
  if (!path) { msg.className='msg err'; msg.textContent='Enter file path'; return; }
  msg.className='msg'; msg.textContent='';
  try {
    const res = await fetch('/api/import-file', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({path, slot})
    });
    const data = await res.json();
    if (res.ok) {
      let txt = '✓ Imported: ' + (data.filename||'ok');
      if (data.report) {
        txt += '\\n' + data.report.total_rows + ' rows';
        if (data.report.by_bu) txt += '\\nBy BU: ' + Object.entries(data.report.by_bu).map(([k,v])=>k+'='+v).join(', ');
      }
      msg.className='msg ok'; msg.style.whiteSpace='pre-line'; msg.textContent=txt;
      loadDatasetStatus();
    } else {
      msg.className='msg err'; msg.textContent='Error: '+(data.detail||'failed');
    }
  } catch(e) { msg.className='msg err'; msg.textContent='Network error'; }
}
</script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML

@app.post("/upload")
async def upload(file: UploadFile = File(...), slot: str = Form("header-logo")):
    is_data_slot = slot.startswith("data-")
    if is_data_slot:
        pass  # accept any file type for data slots
    elif file.content_type not in ALLOWED_TYPES:
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
    # Stream write in chunks for large files
    with open(dest, "wb") as f:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            f.write(chunk)

    # Generate report for CSV data uploads
    report = None
    if is_data_slot and suffix.lower() == '.csv':
        import csv as _csv
        from collections import Counter
        try:
            rows = list(_csv.DictReader(open(dest, encoding='utf-8-sig')))
            total = len(rows)
            report = {"total_rows": total, "filename": dest.name}

            if 'Year' in rows[0] and 'Week' in rows[0]:
                rows2026 = [r for r in rows if r.get('Year') == '2026']
                weeks = sorted(set(r['Week'] for r in rows2026))
                week_detail = {}
                for w in weeks:
                    w_rows = [r for r in rows2026 if r['Week'] == w]
                    bus = Counter(r.get('BU', '?') for r in w_rows)
                    week_detail[f"W{w}"] = {"sites": len(w_rows), "by_bu": dict(bus)}
                report["weeks"] = week_detail
                report["year_rows"] = len(rows2026)
            elif 'OBR BU' in rows[0]:
                bus = Counter(r.get('OBR BU', '?').strip() for r in rows)
                report["by_bu"] = dict(bus)
            elif 'Site' in rows[0]:
                sites = len(set(r.get('Site', '') for r in rows))
                report["unique_sites"] = sites
        except:
            pass

    return {"status": "ok", "filename": dest.name, "report": report}

@app.post("/upload-chunk")
async def upload_chunk(
    file: UploadFile = File(...),
    slot: str = Form("data-inspections"),
    chunk_index: int = Form(0),
    total_chunks: int = Form(1),
    upload_id: str = Form("")
):
    import tempfile
    data_dir = ASSETS_DIR.parent / "data"
    data_dir.mkdir(exist_ok=True)
    tmp_dir = ASSETS_DIR.parent / "tmp_uploads"
    tmp_dir.mkdir(exist_ok=True)

    # Save chunk
    chunk_path = tmp_dir / f"{upload_id}_{chunk_index:04d}"
    with open(chunk_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):
            f.write(chunk)

    # If all chunks received, merge
    if chunk_index == total_chunks - 1:
        dest = data_dir / f"{slot}.csv"
        with open(dest, "wb") as out:
            for i in range(total_chunks):
                cp = tmp_dir / f"{upload_id}_{i:04d}"
                if cp.exists():
                    out.write(cp.read_bytes())
                    cp.unlink()

        # Generate report
        import csv as _csv
        from collections import Counter
        report = {"total_rows": 0, "filename": dest.name}
        try:
            rows = list(_csv.DictReader(open(dest, encoding='utf-8-sig')))
            report["total_rows"] = len(rows)
            if rows and 'OBR BU' in rows[0]:
                report["by_bu"] = dict(Counter(r.get('OBR BU','?').strip() for r in rows))
            elif rows and 'Year' in rows[0]:
                rows2026 = [r for r in rows if r.get('Year')=='2026']
                weeks = sorted(set(r.get('Week','') for r in rows2026))
                report["weeks"] = {f"W{w}": len([r for r in rows2026 if r['Week']==w]) for w in weeks}
        except:
            pass

        return {"status": "ok", "filename": dest.name, "complete": True, "report": report}

    return {"status": "ok", "chunk": chunk_index, "complete": False}


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


def _fmt_date(d):
    """Convert 2026-05-14 to May 14"""
    from datetime import datetime as _dt
    try:
        return _dt.strptime(d, '%Y-%m-%d').strftime('%b %d').replace(' 0', ' ')
    except:
        return d

# ── Dynamic Tables by BU ─────────────────────────────────────────────────────

@app.get("/api/tables")
def get_tables(bu: str = "BR"):
    import csv
    from collections import defaultdict
    from datetime import datetime as dt

    DATA_DIR = ASSETS_DIR.parent / "data"
    BU_MAP_REV = {'BR': None, 'FC': 'LATAMCF', 'SC': 'ATS-LATAM', 'LOG': 'AMZL-LATAM'}
    BU_MAP = {'LATAMCF': 'FC', 'ATS-LATAM': 'SC', 'AMZL-LATAM': 'Logistics'}
    CAT_SEV = {
        'Falling From/Working at Heights': ('A','sev-A'),
        'Electrical': ('A','sev-A'),
        'Chemical Handling/Storage': ('A','sev-A'),
        'Power Industrial Trucks (PIT)': ('B','sev-B'),
        'Trailer Dock Release (TDR)': ('B','sev-B'),
        'Emergency Preparedness': ('B','sev-B'),
        'Product Storage/Falling Object': ('C','sev-C'),
        'Slip/Trip/Fall': ('C','sev-C'),
        'Parking Lot': ('C','sev-C'),
        'Ergonomics': ('D','sev-D'),
        '5S/Housekeeping': ('D','sev-D'),
        'Carts/Cages': ('D','sev-D'),
    }
    SEV_ORDER = {'A':0,'B':1,'C':2,'D':3,'E':4}
    RISK_ORDER = {'Chemical management / Hazardous materials':0,'Chemical (liquid/solid/gas)':0,'Fall Hazard (Gravity)':1,'Materials/Objects & Equipment/Mechanical':2,'Ergonomics':3,'Psychosocial':4}
    REPORT_DATE = dt.now()
    # Dynamic week calculation (last closed week)
    from datetime import timedelta
    day = REPORT_DATE.weekday()  # 0=Mon
    if REPORT_DATE.weekday() == 6:  # Sunday
        last_sun = REPORT_DATE
    else:
        last_sun = REPORT_DATE - timedelta(days=(day + 1))
    last_mon = last_sun - timedelta(days=6)
    W_START = last_mon.strftime('%Y-%m-%d')
    W_END = last_sun.strftime('%Y-%m-%d')

    bu_filter = BU_MAP_REV.get(bu)

    # Near Miss + Critical Events — try data-nearmiss.csv (individual) first, fallback to data-incidents.csv (aggregated)
    nm_results = []
    crit_events = []
    nm_file = DATA_DIR / "data-nearmiss.csv"
    if not nm_file.exists():
        nm_file = DATA_DIR / "data-incidents.csv"
    if nm_file.exists():
        inc = list(csv.DictReader(open(nm_file, encoding='utf-8-sig')))

        # Detect format: aggregated (Year-Week) vs individual (Incident Date)
        if inc and 'Year-Week' in inc[0]:
            # New aggregated format
            # Determine week string (e.g. "2026-21")
            from datetime import timedelta
            week_num = last_mon.isocalendar()[1]
            week_str = f"{last_mon.year}-{week_num}"
            w_rows = [r for r in inc if r.get('Year-Week','').strip() == week_str]
            if bu_filter:
                w_rows = [r for r in w_rows if r.get('OBR BU','').strip() == bu_filter]

            # Near Miss: sites with NM > 0
            nm_sites = [r for r in w_rows if int(r.get('Near Miss Count','0') or 0) > 0]
            nm_sites.sort(key=lambda r: -int(r.get('Near Miss Count','0') or 0))
            for r in nm_sites[:10]:
                nm_count = int(r.get('Near Miss Count','0') or 0)
                nm_results.append({
                    'site': r.get('Site',''),
                    'bu': BU_MAP.get(r.get('OBR BU','').strip(), r.get('OBR BU','')),
                    'risk': f"{nm_count} near miss events",
                    'date': r.get('Year-Week',''),
                    'desc': f"{nm_count} near miss events recorded at {r.get('Site','')} this week"
                })

            # Critical Events: sites with SI or RI > 0
            crit_sites = [r for r in w_rows if int(r.get('SI Count','0') or 0) > 0 or int(r.get('RI Count','0') or 0) > 0]
            for r in crit_sites:
                si = int(r.get('SI Count','0') or 0)
                ri = int(r.get('RI Count','0') or 0)
                evt_type = []
                if si > 0: evt_type.append(f"{si} SI")
                if ri > 0: evt_type.append(f"{ri} RI")
                crit_events.append({
                    'site': r.get('Site',''),
                    'bu': BU_MAP.get(r.get('OBR BU','').strip(), r.get('OBR BU','')),
                    'type': ' + '.join(evt_type),
                    'sev': 'A' if si > 0 else 'B',
                    'date': r.get('Year-Week',''),
                    'desc': f"{' + '.join(evt_type)} at {r.get('Site','')} in {r.get('Year-Week','')}"
                })
        else:
            # Individual format (Incident Date, Description, Severity)
            week_inc = [r for r in inc if W_START <= r.get('Incident Date','')[:10] <= W_END]
            if bu_filter:
                week_inc = [r for r in week_inc if r.get('OBR BU','').strip() == bu_filter]

            # Near Miss (Near Miss Ind=1 OR Severity D/PENDING — minor events)
            nm_rows = [r for r in week_inc if r.get('Near Miss Incident Ind','0')=='1'
                       or r.get('Severity','').strip() in ('D','PENDING')]
            nm_rows.sort(key=lambda r: (RISK_ORDER.get(r.get('Risk Category','').strip(),9), r.get('Incident Date','')))
            for r in nm_rows[:10]:
                nm_results.append({
                    'site': r.get('Site',''),
                    'bu': BU_MAP.get(r.get('OBR BU','').strip(), r.get('OBR BU','')),
                    'risk': (r.get('Risk Category','') or '—')[:40],
                    'date': _fmt_date(r.get('Incident Date','')[:10]),
                    'desc': r.get('Description','')[:250]
                })

            # Critical Events (Severity A or B)
            crit_rows = [r for r in week_inc if r.get('Severity','').strip() in ('A','B')]
            crit_rows.sort(key=lambda r: r.get('Severity',''))
            for r in crit_rows:
                crit_events.append({
                    'site': r.get('Site',''),
                    'bu': BU_MAP.get(r.get('OBR BU','').strip(), r.get('OBR BU','')),
                    'type': f"Severity {r.get('Severity','').strip()}",
                    'sev': r.get('Severity','').strip(),
                    'date': _fmt_date(r.get('Incident Date','')[:10]),
                    'desc': r.get('Description','')[:250]
                })

    # Critical Observations
    crit_results = []
    dfy_file = DATA_DIR / "data-dragonfly.csv"
    if dfy_file.exists():
        dfy = list(csv.DictReader(open(dfy_file, encoding='utf-8-sig')))
        week20 = [r for r in dfy if W_START <= r.get('Finding Creation Timestamp (UTC)','')[:10] <= W_END]
        major = [r for r in week20 if r.get('Severity (AI)','')=='4' and r.get('Closure Status','').strip()=='Open']
        if bu_filter:
            major = [r for r in major if r.get('OBR BU','').strip() == bu_filter]

        for r in major:
            date_str = r.get('Finding Creation Timestamp (UTC)','')[:10]
            try: r['_days'] = (REPORT_DATE - dt.strptime(date_str, '%Y-%m-%d')).days
            except: r['_days'] = 0
            r['_sev_order'] = SEV_ORDER.get(CAT_SEV.get(r.get('Category (AI)',''), ('E',''))[0], 9)

        major.sort(key=lambda r: (r['_sev_order'], -r['_days']))

        for r in major[:12]:
            cat = r.get('Category (AI)','—')
            _, sev_css = CAT_SEV.get(cat, ('C','sev-C'))
            crit_results.append({
                'site': r.get('Site',''),
                'bu': BU_MAP.get(r.get('OBR BU','').strip(), r.get('OBR BU','')),
                'observer': r.get('Submitter Login',''),
                'category': cat,
                'sev_css': sev_css,
                'date': _fmt_date(r.get('Finding Creation Timestamp (UTC)','')[:10]),
                'days': r['_days'],
                'obs': r.get('Safety Observation','')[:250]
            })

    # Translate and summarize descriptions to English
    if CLAUDE_API_KEY and (nm_results or crit_results or crit_events):
        try:
            all_descs = [r['desc'] for r in nm_results] + [r['obs'] for r in crit_results] + [r['desc'] for r in crit_events]
            batch = '\n---\n'.join(f'[{i}] {t}' for i,t in enumerate(all_descs) if t)
            client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
            resp = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=3000,
                messages=[{"role": "user", "content": f"Translate and summarize each numbered safety observation below from Portuguese to English. Make each ONE clear sentence (max 25 words). Keep numbering. Output only translations:\n\n{batch}"}]
            )
            lines = resp.content[0].text.strip().split('\n')
            translations = {}
            for line in lines:
                line = line.strip()
                if line.startswith('['):
                    try:
                        idx = int(line[1:line.index(']')])
                        translations[idx] = line[line.index(']')+1:].strip()
                    except: pass
            for i, r in enumerate(nm_results):
                if i in translations: r['desc'] = translations[i]
            nm_len = len(nm_results)
            for i, r in enumerate(crit_results):
                if (nm_len + i) in translations: r['obs'] = translations[nm_len + i]
            evt_offset = nm_len + len(crit_results)
            for i, r in enumerate(crit_events):
                if (evt_offset + i) in translations: r['desc'] = translations[evt_offset + i]
        except Exception as e:
            pass  # keep originals if translation fails

    return {"near_miss": nm_results, "critical_obs": crit_results, "critical_events": crit_events, "bu": bu}


# ── Import Large File ─────────────────────────────────────────────────────────

class ImportRequest(BaseModel):
    path: str
    slot: str

@app.post("/api/import-file")
def import_file(req: ImportRequest):
    import csv as _csv, shutil, os
    from collections import Counter
    from pathlib import Path as _Path

    # Resolve path
    src = _Path(req.path.replace('~', str(_Path.home()))).expanduser()
    if not src.exists():
        raise HTTPException(400, f"File not found: {src}")
    if req.slot not in SLOTS:
        raise HTTPException(400, "Invalid slot.")

    data_dir = ASSETS_DIR.parent / "data"
    data_dir.mkdir(exist_ok=True)
    dest = data_dir / f"{req.slot}.csv"

    # Copy file
    shutil.copy2(str(src), str(dest))

    # Generate report
    report = {"total_rows": 0, "filename": dest.name}
    try:
        rows = list(_csv.DictReader(open(dest, encoding='utf-8-sig')))
        report["total_rows"] = len(rows)
        if rows and 'OBR BU' in rows[0]:
            bus = Counter(r.get('OBR BU', '?').strip() for r in rows)
            report["by_bu"] = dict(bus)
        elif rows and 'Year' in rows[0]:
            rows2026 = [r for r in rows if r.get('Year') == '2026']
            weeks = sorted(set(r.get('Week','') for r in rows2026))
            report["year_rows"] = len(rows2026)
            report["weeks"] = {f"W{w}": len([r for r in rows2026 if r['Week']==w]) for w in weeks}
        elif rows and 'Site' in rows[0]:
            report["unique_sites"] = len(set(r.get('Site','') for r in rows))
    except:
        pass

    return {"status": "ok", "filename": dest.name, "report": report}


# ── Best Dragonfly ────────────────────────────────────────────────────────────

@app.get("/api/best-dragonfly")
def get_best_dragonfly(week: str = "", bu: str = ""):
    import csv
    from collections import Counter
    from datetime import datetime as dt, timedelta

    DATA_DIR = ASSETS_DIR.parent / "data"
    DFY_FILE = DATA_DIR / "data-dragonfly.csv"
    if not DFY_FILE.exists():
        return {"items": []}

    # Determine week range
    if not week:
        # Use latest closed week
        now = dt.now()
        day = now.weekday()  # 0=Mon
        if now.weekday() == 6:  # Sunday
            last_sun = now
        else:
            last_sun = now - timedelta(days=(now.weekday() + 1))
        last_mon = last_sun - timedelta(days=6)
        w_start = last_mon.strftime('%Y-%m-%d')
        w_end = last_sun.strftime('%Y-%m-%d')
    else:
        # Parse week string like "2026-W21"
        year, wn = int(week.split('-W')[0]), int(week.split('-W')[1])
        jan4 = dt(year, 1, 4)
        start_w1 = jan4 - timedelta(days=((jan4.weekday()) % 7))
        last_mon = start_w1 + timedelta(weeks=wn-1)
        w_end = (last_mon + timedelta(days=6)).strftime('%Y-%m-%d')
        w_start = last_mon.strftime('%Y-%m-%d')

    dfy = list(csv.DictReader(open(DFY_FILE, encoding='utf-8-sig')))
    week_rows = [r for r in dfy if w_start <= r.get('Finding Creation Timestamp (UTC)','')[:10] <= w_end]

    BU_MAP = {'LATAMCF': 'Fulfillment Center', 'ATS-LATAM': 'Sort Center', 'AMZL-LATAM': 'Logistics'}
    BU_FILTER_MAP = {'FC': 'LATAMCF', 'SC': 'ATS-LATAM', 'LOG': 'AMZL-LATAM'}

    # Filter by BU if specified
    if bu and bu in BU_FILTER_MAP:
        bu_code = BU_FILTER_MAP[bu]
        week_rows = [r for r in week_rows if r.get('OBR BU','').strip() == bu_code]

    # Top submitters per BU + overall best
    submitters = Counter()
    submitter_info = {}
    for r in week_rows:
        login = r.get('Submitter Login','').strip()
        if not login:
            continue
        submitters[login] += 1
        obs_text = r.get('Safety Observation','').strip()[:200]
        if login not in submitter_info:
            submitter_info[login] = {
                'site': r.get('Site',''),
                'bu': r.get('OBR BU','').strip(),
                'last_date': r.get('Finding Creation Timestamp (UTC)','')[:10],
                'observation': obs_text,
            }
        if r.get('Finding Creation Timestamp (UTC)','')[:10] >= submitter_info[login]['last_date']:
            submitter_info[login]['last_date'] = r.get('Finding Creation Timestamp (UTC)','')[:10]
            if obs_text:
                submitter_info[login]['observation'] = obs_text

    if not submitters:
        return {"items": [], "week_start": w_start, "week_end": w_end}

    # Best overall
    best_overall = submitters.most_common(1)[0]

    # Best per BU (excluding overall winner for variety)
    items = []
    # Add best overall
    login, count = best_overall
    info = submitter_info[login]
    items.append({
        "badge": "Best Brazil",
        "bu_label": BU_MAP.get(info['bu'], info['bu']),
        "site": info['site'],
        "login": login,
        "obs_count": count,
        "date": info['last_date'],
        "observation": info.get('observation', ''),
    })

    # Best per BU (different from overall)
    for bu_code, bu_label in BU_MAP.items():
        bu_subs = [(l, c) for l, c in submitters.most_common(20) if submitter_info[l]['bu'] == bu_code and l != best_overall[0]]
        if bu_subs:
            login, count = bu_subs[0]
            info = submitter_info[login]
            items.append({
                "badge": None,
                "bu_label": bu_label,
                "site": info['site'],
                "login": login,
                "obs_count": count,
                "date": info['last_date'],
                "observation": info.get('observation', ''),
            })

    # Translate observations to English
    items = items[:4]
    if any(i.get('observation') for i in items):
        try:
            obs_texts = [i.get('observation','') for i in items if i.get('observation')]
            batch = '\n'.join(f'[{idx}] {t}' for idx, t in enumerate(obs_texts))
            client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
            resp = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=1000,
                messages=[{"role": "user", "content": f"Translate each numbered safety observation to English. Make each ONE clear sentence (max 25 words). Keep numbering. Output only translations:\n\n{batch}"}]
            )
            translations = {}
            for line in resp.content[0].text.strip().split('\n'):
                line = line.strip()
                if line.startswith('['):
                    try:
                        idx = int(line[1:line.index(']')])
                        translations[idx] = line[line.index(']')+1:].strip()
                    except: pass
            obs_idx = 0
            for i in items:
                if i.get('observation'):
                    if obs_idx in translations:
                        i['observation'] = translations[obs_idx]
                    obs_idx += 1
        except Exception as e:
            import traceback
            traceback.print_exc()

    return {"items": items, "week_start": w_start, "week_end": w_end}


# ── Dataset Status ────────────────────────────────────────────────────────────

@app.get("/api/datasets")
def get_datasets_status():
    from datetime import datetime, timezone
    import os

    DATA_DIR = ASSETS_DIR.parent / "data"
    datasets = {
        "data-flash-report": "Flash Report CSV",
        "data-incidents": "Incidents CSV",
        "data-nearmiss": "Near Miss CSV",
        "data-dragonfly": "Dragonfly CSV",
    }
    result = []
    for key, label in datasets.items():
        path = DATA_DIR / f"{key}.csv"
        if path.exists():
            mtime = os.path.getmtime(path)
            dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
            size_kb = path.stat().st_size / 1024
            result.append({"key": key, "label": label, "updated": dt.isoformat(), "size_kb": round(size_kb, 1), "exists": True})
        else:
            result.append({"key": key, "label": label, "updated": None, "size_kb": 0, "exists": False})
    return {"datasets": result}


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
    # Filter to 2026 only
    rows = [r for r in rows if r.get('Year','') == '2026']
    weeks = sorted(set(r['Week'] for r in rows if r.get('Week','')))
    if not weeks:
        raise HTTPException(400, "No week data found in CSV for 2026.")
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
        insp_otc_w_vals = [sf(r.get('INSP_OTC_Week','')) for r in bu_rows if sf(r.get('INSP_OTC_Week','')) > 0]
        insp_otc_w_avg = sum(insp_otc_w_vals) / len(insp_otc_w_vals) * 100 if insp_otc_w_vals else 0
        insp_otc_y_num = sum(sf(r.get('INSP_Inspection_OTC','')) * sf(r.get('INSP_Due_Inspections','')) for r in bu_rows)
        insp_otc_y_den = sum(sf(r.get('INSP_Due_Inspections','')) for r in bu_rows if sf(r.get('INSP_Inspection_OTC','')) > 0)
        insp_otc_y_avg = (insp_otc_y_num / insp_otc_y_den * 100) if insp_otc_y_den > 0 else 0
        # Actions OTC
        act_otc_w_vals = [sf(r.get('INSP_Task_OTC_Week','')) for r in bu_rows if sf(r.get('INSP_Task_OTC_Week','')) > 0]
        act_otc_w_avg = sum(act_otc_w_vals) / len(act_otc_w_vals) * 100 if act_otc_w_vals else 0
        act_otc_y_num = sum(sf(r.get('INSP_Task_OTC','')) * sf(r.get('INSP_Due_Tasks','')) for r in bu_rows)
        act_otc_y_den = sum(sf(r.get('INSP_Due_Tasks','')) for r in bu_rows if sf(r.get('INSP_Task_OTC','')) > 0)
        act_otc_y_avg = (act_otc_y_num / act_otc_y_den * 100) if act_otc_y_den > 0 else 0
        return {
            'sir': (fmt(rate(si_w,h_w)), fmt(rate(si_y,h_y))),
            'rir': (fmt(rate(ri_w,h_w)), fmt(rate(ri_y,h_y))),
            'ltir': (fmt(rate(lti_w,h_w)), fmt(rate(lti_y,h_y))),
            'fair': (fmt(rate(fai_w,h_w)), fmt(rate(fai_y,h_y))),
            'dfy_rate': (fmt(rate(dfy_obs_w,h_w),1), fmt(rate(dfy_obs_y,h_y),1)),
            'dfy_closure': (fmt_pct(pct(dfy_closed_w,dfy_obs_w)), fmt_pct(pct(dfy_closed_y,dfy_obs_y))),
            'insp_otc': (fmt_pct(insp_otc_w_avg), fmt_pct(insp_otc_y_avg)),
            'act_otc': (fmt_pct(act_otc_w_avg), fmt_pct(act_otc_y_avg)),
            'nm': (str(int(nm_w)), str(int(nm_y))),
        }

    fc_w = [r for r in week_rows if r['BU']=='LATAMCF']
    sc_w = [r for r in week_rows if r['BU']=='ATS-LATAM']
    log_w = [r for r in week_rows if r['BU']=='AMZL-LATAM']
    fc_all = [r for r in rows if r['BU']=='LATAMCF']
    sc_all = [r for r in rows if r['BU']=='ATS-LATAM']
    log_all = [r for r in rows if r['BU']=='AMZL-LATAM']

    # DFY On-time Closure Rate from dragonfly CSV
    from datetime import datetime as _dt
    DFY_FILE = DATA_DIR / "data-dragonfly.csv"
    dfy_closure_rates = {}
    if DFY_FILE.exists():
        dfy_rows = list(csv.DictReader(open(DFY_FILE, encoding='utf-8-sig')))
        w_start = f'2026-{int(latest_week):02d}'
        # Determine week date range
        from datetime import timedelta
        jan4 = _dt(2026, 1, 4)
        week1_start = jan4 - timedelta(days=(jan4.weekday()))
        wk_start_date = week1_start + timedelta(weeks=int(latest_week)-1)
        wk_end_date = wk_start_date + timedelta(days=6)
        W_START = wk_start_date.strftime('%Y-%m-%d')
        W_END = wk_end_date.strftime('%Y-%m-%d')

        def calc_dfy_closure(dfy_list, week_start, week_end):
            on_time_y, late_y = 0, 0
            # Week: obs whose due date falls in the week (not created in the week)
            on_time_w, miss_w = 0, 0
            for r in dfy_list:
                due = r.get('Due Date TImestamp (UTC)','').strip()[:10]
                completed = r.get('Completion Timestamp (UTC)','').strip()[:10]
                if not due:
                    continue
                due_in_week = week_start <= due <= week_end
                if due_in_week:
                    if completed:
                        try:
                            if _dt.strptime(completed, '%Y-%m-%d') <= _dt.strptime(due, '%Y-%m-%d'):
                                on_time_w += 1
                            else:
                                miss_w += 1
                        except:
                            miss_w += 1
                    else:
                        miss_w += 1  # open past due = miss
                # YTD: all obs that have been closed
                if completed:
                    try:
                        if _dt.strptime(completed, '%Y-%m-%d') <= _dt.strptime(due, '%Y-%m-%d'):
                            on_time_y += 1
                        else:
                            late_y += 1
                    except:
                        pass
            total_y = on_time_y + late_y
            total_w = on_time_w + miss_w
            rate_y = fmt_pct(on_time_y / total_y * 100) if total_y > 0 else '0.0%'
            rate_w = fmt_pct(on_time_w / total_w * 100) if total_w > 0 else '0.0%'
            return (rate_w, rate_y)

        dfy_closure_rates['Brazil'] = calc_dfy_closure(dfy_rows, W_START, W_END)
        dfy_closure_rates['FC'] = calc_dfy_closure([r for r in dfy_rows if r.get('OBR BU','').strip()=='LATAMCF'], W_START, W_END)
        dfy_closure_rates['SC'] = calc_dfy_closure([r for r in dfy_rows if r.get('OBR BU','').strip()=='ATS-LATAM'], W_START, W_END)
        dfy_closure_rates['Logistics'] = calc_dfy_closure([r for r in dfy_rows if r.get('OBR BU','').strip()=='AMZL-LATAM'], W_START, W_END)

    agg = {
        'Brazil': calc_bu(week_rows, rows),
        'FC': calc_bu(fc_w, fc_all),
        'SC': calc_bu(sc_w, sc_all),
        'Logistics': calc_bu(log_w, log_all),
    }
    # Override dfy_closure with on-time calculation
    for bu_key in dfy_closure_rates:
        if bu_key in agg:
            agg[bu_key]['dfy_closure'] = dfy_closure_rates[bu_key]

    # Patch HTML
    html = HTML_FILE.read_text(encoding='utf-8')

    LABEL_TO_KEY = {
        'Serious Incident Rate': 'sir',
        'Recordable Incident Rate': 'rir',
        'Lost Time Incident Rate': 'ltir',
        'First Aid Rate': 'fair',
        'Dragonfly Rate': 'dfy_rate',
        'Dragonfly OTC': 'dfy_closure',
        'Inspection OTC': 'insp_otc',
        'Actions OTC': 'act_otc',
        'Near Miss': 'nm',
    }
    COL_CLASS_TO_BU = {'hl': 'Brazil', 'fc': 'FC', 'sc': 'SC', 'log': 'Logistics'}

    col_pattern = re.compile(r'<div class="metrics-col\s+(\w+)">')
    card_pattern = re.compile(
        r'<div class="metric-lbl">([^<]+)</div>'
        r'.*?<div class="metric-wk">([^<]*)</div>'
        r'.*?<div class="metric-ytd-val">([^<]*)</div>',
        re.DOTALL
    )

    def patch_section(html, pill_text):
        start = html.find(f'<span class="pill">{pill_text}</span>')
        if start == -1:
            return html
        end = html.find('<div style="height:3px', start)
        if end == -1:
            end = html.find('<div class="hl-grid"', start)
        if end == -1:
            return html
        chunk = html[start:end]

        # Split by column divs to identify which BU each card belongs to
        col_splits = list(col_pattern.finditer(chunk))
        # Process columns in reverse order so earlier offsets stay valid
        for col_idx in range(len(col_splits) - 1, -1, -1):
            col_match = col_splits[col_idx]
            col_class = col_match.group(1)
            bu_key = COL_CLASS_TO_BU.get(col_class)
            if not bu_key:
                continue

            # Determine the range for this column within the chunk
            col_start = col_match.start()
            col_end = col_splits[col_idx + 1].start() if col_idx + 1 < len(col_splits) else len(chunk)
            col_html = chunk[col_start:col_end]

            # Find all cards in this column and patch them by label
            new_col_html = col_html
            for card_m in list(card_pattern.finditer(col_html)):
                label = card_m.group(1).strip()
                metric_key = LABEL_TO_KEY.get(label)
                if metric_key and metric_key in agg.get(bu_key, {}):
                    w, y = agg[bu_key][metric_key]
                    old_fragment = card_m.group(0)
                    new_fragment = old_fragment
                    # Replace week value
                    new_fragment = re.sub(
                        r'(<div class="metric-wk">)[^<]*(</div>)',
                        rf'\g<1>{w}\2',
                        new_fragment,
                        count=1
                    )
                    # Replace YTD value
                    new_fragment = re.sub(
                        r'(<div class="metric-ytd-val">)[^<]*(</div>)',
                        rf'\g<1>{y}\2',
                        new_fragment,
                        count=1
                    )
                    new_col_html = new_col_html.replace(old_fragment, new_fragment, 1)

            chunk = chunk[:col_start] + new_col_html + chunk[col_end:]

        return html[:start] + chunk + html[end:]

    html = patch_section(html, 'Events')
    html = patch_section(html, 'Barriers')

    # Update week references
    html = re.sub(r'Week 2026-W\d+', f'Week 2026-W{latest_week}', html)

    HTML_FILE.write_text(html, encoding='utf-8')
    if PUBLIC_FILE.parent.exists():
        PUBLIC_FILE.write_text(html, encoding='utf-8')

    # Report missing sites (sites that existed in previous weeks but not in latest)
    all_sites = set(r['Site'] for r in rows)
    latest_sites = set(r['Site'] for r in week_rows)
    missing = sorted(all_sites - latest_sites)

    return {
        "ok": True,
        "detail": f"Week {latest_week} — {len(week_rows)} sites updated",
        "week": latest_week,
        "sites_count": len(week_rows),
        "missing_sites": missing,
        "missing_count": len(missing),
    }


# ── Claude AI Insights ────────────────────────────────────────────────────────

class InsightsRequest(BaseModel):
    bu: str          # "Brazil Operations" | "Fulfillment Centers" | "Sort Centers" | "Logistics"
    section: str     # "events" | "barriers"
    metrics: dict    # {metric_name: {week: val, ytd: val}, ...}

class SnapRequest(BaseModel):
    field: str
    prompt: str

# Verified facts from aboutamazon.com/news (2025 safety report) + public data
DID_YOU_KNOW_FACTS = [
    "Amazon's Global Recordable Incident Rate improved 43% over six years and 14% year-over-year (2025 report).",
    "Amazon's Global Lost Time Incident Rate improved 70% over six years (2019–2025).",
    "Amazon invested over $2.5 billion in safety innovations, ergonomic improvements, and training since 2019.",
    "Amazon conducted 10.4 million safety inspections globally in 2025 — a 33% increase from the previous year.",
    "More than 200,000 Amazon employees used the Dragonfly tool to submit safety observations in 2025.",
    "Amazon employs more than 11,000 safety professionals across more than 2,000 sites globally.",
    "Musculoskeletal disorders (MSDs) account for more than half of all recordable injuries at Amazon; MSD rate improved 43% over six years.",
    "Amazon's U.S. Courier and Express Delivery LTIR improved 81% over six years and 28% year-over-year.",
    "Amazon's U.S. General Warehousing RIR improved 39% over six years and 16% year-over-year.",
    "More than 180,000 delivery drivers completed in-person training at Amazon's Integrated Last Mile Driver Academy.",
    "Amazon received eight safety awards in 2025 from the American Red Cross, British Safety Council, National Safety Council, and Applied Ergonomics Society.",
    "Amazon achieved the highest three-star rating in the FIA Road Safety Index.",
    "Amazon rolled out more than 30,000 custom electric delivery vans (Rivian) across the U.S., improving driver ergonomics.",
    "Amazon committed hundreds of millions in 2026 for safety innovation, training, and program expansion.",
    "Amazon's operations network has more than doubled in size since 2019 while injury rates continued to decline.",
]

@app.post("/api/snap")
async def generate_snap(req: SnapRequest):
    import csv, random
    from collections import defaultdict

    # Did You Know: return 3 verified facts for user to pick (no AI, zero hallucination)
    if req.field == 'did_you_know':
        import random as _rnd
        facts = _rnd.sample(DID_YOU_KNOW_FACTS, min(3, len(DID_YOU_KNOW_FACTS)))
        return {"text": facts[0], "options": facts}

    DATA_DIR = ASSETS_DIR.parent / "data"
    BU_MAP_REV = {'BR': None, 'FC': 'LATAMCF', 'SC': 'ATS-LATAM', 'LOG': 'AMZL-LATAM'}

    # Build real context from 2026 data
    context_lines = []
    flash_csv = DATA_DIR / "data-flash-report.csv"
    if flash_csv.exists():
        rows = list(csv.DictReader(open(flash_csv, encoding='utf-8-sig')))
        rows = [r for r in rows if r.get('Year') == '2026']
        weeks = sorted(set(r['Week'] for r in rows))
        latest_week = weeks[-1] if weeks else '20'
        week_rows = [r for r in rows if r['Week'] == latest_week]

        # Filter by BU if specified in prompt
        bu_filter = None
        for key, val in BU_MAP_REV.items():
            if val and val.lower() in req.prompt.lower():
                bu_filter = val
                break
        if bu_filter:
            week_rows = [r for r in week_rows if r.get('BU') == bu_filter]

        def sf(v):
            try: return float(str(v).strip().replace(',','.')) if v and str(v).strip() else 0.0
            except: return 0.0

        # Top sites by hours (relevance)
        site_data = []
        for r in sorted(week_rows, key=lambda x: -sf(x.get('Total_Hours_Week','0')))[:10]:
            site = r['Site']
            hours = sf(r['Total_Hours_Week'])
            ri = int(sf(r.get('INC_RI_Week','0')))
            lti = int(sf(r.get('INC_LTI_Week','0')))
            fai = int(sf(r.get('INC_FAI_Week','0')))
            nm = int(sf(r.get('INC_Near_Miss_Week','0')))
            dfy = int(sf(r.get('DFY_Total_Obs_Week','0')))
            site_data.append(f"{site}: {hours:.0f}h, RI={ri}, LTI={lti}, FAI={fai}, NM={nm}, DFY_obs={dfy}")

        if site_data:
            context_lines.append(f"REAL DATA Week {latest_week} (2026) — top sites by volume:")
            context_lines.extend(site_data)

    # Dragonfly highlights
    dfy_file = DATA_DIR / "data-dragonfly.csv"
    if dfy_file.exists():
        dfy_rows = list(csv.DictReader(open(dfy_file, encoding='utf-8-sig')))
        # Top submitters this week
        from collections import Counter
        from datetime import timedelta as _td
        _now = __import__('datetime').datetime.now()
        _day = _now.weekday()
        _last_sun = _now if _day == 6 else _now - _td(days=(_day + 1))
        _last_mon = _last_sun - _td(days=6)
        _w_start = _last_mon.strftime('%Y-%m-%d')
        _w_end = _last_sun.strftime('%Y-%m-%d')
        week_dfy = [r for r in dfy_rows if _w_start <= r.get('Finding Creation Timestamp (UTC)','')[:10] <= _w_end]
        if bu_filter:
            week_dfy = [r for r in week_dfy if r.get('OBR BU','').strip() == bu_filter]
        submitters = Counter(r.get('Submitter Login','') for r in week_dfy if r.get('Submitter Login',''))
        top_sub = submitters.most_common(3)
        if top_sub:
            context_lines.append(f"Top Dragonfly submitters this week: {', '.join(f'@{s} ({c} obs)' for s,c in top_sub)}")

    context = '\n'.join(context_lines)
    full_prompt = f"""{req.prompt}

GLOSSARY: RI=Recordable Incident, LTI=Lost Time Injury, FAI=First Aid Incident, NM=Near Miss, DFY_obs=Dragonfly safety observations, h=exposure hours

DATA (this is the ONLY source of truth — every claim must trace to a number here):
{context}

ABSOLUTE RULES:
1. ZERO hallucination — every single number, site name, and fact MUST come directly from the DATA above
2. Do NOT infer, assume, or add information not explicitly in the data (no "requiring review", no "demonstrating excellence", no opinions)
3. Do NOT mention actions taken, recommendations, or causes — only state what the numbers show
4. If you cannot write the sentence using ONLY data above, write "No data available"
5. Format: state the fact with the exact number. Example: "GRU8 had 7 FAI in Week 20." — nothing more
6. Year is 2026 — never reference other years"""

    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": full_prompt}]
    )
    return {"text": response.content[0].text.strip()}


# ── Email Generation ──────────────────────────────────────────────────────────

class EmailRequest(BaseModel):
    week: str
    bu: str
    summary: str = ""
    recipients: str = ""
    lang: str = "EN"

@app.post("/api/report/email")
async def generate_email(req: EmailRequest):
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
    import json as _json

    states = load_states()
    entry = states.get(req.week, {}).get(req.bu, {})
    content = entry.get("content", {})
    submitted_by = entry.get("submitted_by", "WHS Team")
    bu_name = BU_LABELS.get(req.bu, "Brazil Operations")

    # Build summary from saved content if not provided
    summary_text = req.summary
    if not summary_text:
        parts = []
        if content.get("hot_flag"):
            parts.append(f"Hot Flag: {content['hot_flag'].replace('<strong>','').replace('</strong>','')}")
        for i in range(3):
            hl = content.get(f"ev_hl_{i}", "")
            if hl:
                parts.append(f"+ {hl}")
        for i in range(3):
            ll = content.get(f"ev_ll_{i}", "")
            if ll:
                parts.append(f"- {ll}")
        summary_text = "\n".join(parts) if parts else "Flash Report published. See attachment for full details."

    hot_flag = content.get('hot_flag', '')
    hot_flag_html = ''
    if hot_flag:
        hot_flag_clean = hot_flag.replace('<strong>', '<strong style="color:#c62828">').replace('</strong>', '</strong>')
        hot_flag_html = f"""
  <tr>
    <td style="padding:0 36px 20px">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#fff5f5;border-radius:10px;border-left:4px solid #e53935">
        <tr><td style="padding:14px 18px">
          <span style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:1px;color:#e53935">&#9873; Hot Flag</span>
          <p style="font-size:13px;color:#555;line-height:1.6;margin:8px 0 0">{hot_flag_clean}</p>
        </td></tr>
      </table>
    </td>
  </tr>"""

    # Format summary as clean paragraph (no bullets)
    summary_clean = summary_text.replace('\n', ' ').strip()

    # Use absolute URLs for logos (accessible via DevSpaces proxy with Midway)
    asset_url = "https://ds-akyj2d5n--3003.us-east-1.prod.proxy.devspaces.amazon.dev/assets"
    logo_header = f"{asset_url}/header-logo.png"
    logo_footer = f"{asset_url}/footer-logo.png"
    logo_safetogo = f"{asset_url}/safetogo-logo.png"
    logo_amazon = f"{asset_url}/amazon-logo.png"

    email_html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;font-family:'Segoe UI',Arial,Helvetica,sans-serif;background:#f2f2f2">
<table width="100%" cellpadding="0" cellspacing="0" style="max-width:640px;margin:0 auto;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08)">

  <!-- HEADER (replica do Flash Report) -->
  <tr>
    <td style="background:#3D3D3D;background:linear-gradient(135deg,#3D3D3D 0%,#555555 50%,#686868 100%);padding:24px 32px;min-height:110px">
      <table cellpadding="0" cellspacing="0" width="100%"><tr>
        <td style="vertical-align:middle;width:80px">
          <img src="{logo_header}" alt="WHS Brazil" style="height:64px;max-width:160px;object-fit:contain;display:block">
        </td>
        <td style="vertical-align:middle;padding-left:16px">
          <span style="font-size:10px;text-transform:uppercase;letter-spacing:2.5px;color:rgba(255,255,255,0.5);display:block">WHS Brazil</span>
          <span style="font-size:26px;font-weight:900;color:#ffffff;letter-spacing:-0.5px;display:block;margin-top:2px;font-family:'Segoe UI',Arial,sans-serif">Flash Report</span>
          <span style="font-size:11px;color:rgba(255,255,255,0.3);display:block;margin-top:3px">{req.week}</span>
        </td>
        <td style="vertical-align:middle;text-align:right">
          <img src="{logo_safetogo}" alt="Safe to Go" style="height:32px;max-width:120px;object-fit:contain;display:inline-block;margin-right:12px;position:relative;top:-3px">
          <img src="{logo_amazon}" alt="Amazon" style="height:24px;max-width:90px;object-fit:contain;display:inline-block">
        </td>
      </tr></table>
    </td>
  </tr>

  <!-- BU + AUTHOR -->
  <tr>
    <td style="padding:24px 36px 0">
      <span style="background:#f0faf4;border:1.5px solid #8FD44F;color:#2d5a1e;font-size:12px;font-weight:700;padding:6px 16px;border-radius:20px;display:inline-block">{bu_name}</span>
      <span style="font-size:12px;color:#aaa;margin-left:10px">by <strong style="color:#555">{submitted_by}</strong></span>
    </td>
  </tr>

  <!-- STORYTELLING PARAGRAPH -->
  <tr>
    <td style="padding:24px 36px">
      <p style="font-size:14px;color:#333;line-height:1.85;margin:0">{summary_clean}</p>
    </td>
  </tr>

  <!-- HOT FLAG (if any) -->
  {hot_flag_html}

  <!-- ATTACHMENT NOTE -->
  <tr>
    <td style="padding:8px 36px 28px">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr><td style="text-align:center;padding-bottom:16px">
          <a href="https://ds-akyj2d5n--3000.us-east-1.prod.proxy.devspaces.amazon.dev/flash-report.html?mode=view&bu={req.bu}&week={req.week}" style="display:inline-block;background:linear-gradient(135deg,#8FD44F,#A8D8A8);color:#2d4a1e;font-size:13px;font-weight:800;padding:12px 28px;border-radius:24px;text-decoration:none;letter-spacing:0.3px">View Full Report Online</a>
        </td></tr>
        <tr><td style="text-align:center">
          <span style="font-size:11px;color:#aaa">or open the attached HTML file in any browser</span>
        </td></tr>
      </table>
    </td>
  </tr>

  <!-- FOOTER -->
  <tr>
    <td style="background:#fafafa;border-top:1px solid #eee;padding:18px 36px">
      <table cellpadding="0" cellspacing="0" width="100%"><tr>
        <td style="vertical-align:middle;width:50px">
          <img src="{logo_footer}" alt="WHS" style="height:42px;object-fit:contain;display:block;opacity:0.6">
        </td>
        <td style="vertical-align:middle;text-align:right">
          <span style="font-size:10px;color:#ccc;letter-spacing:0.5px">Powered by <strong style="color:#8FD44F">AIRA</strong> | Amazon Risk Intelligence Agent - WHS Brazil</span>
        </td>
      </tr></table>
    </td>
  </tr>

</table>
</body>
</html>"""

    # Build .eml with attachment
    msg = MIMEMultipart('mixed')
    msg['Subject'] = f"Flash Report - {bu_name} - {req.week}"
    msg['From'] = f"{submitted_by}@amazon.com"
    msg['To'] = req.recipients or ""

    # HTML body
    html_part = MIMEText(email_html, 'html', 'utf-8')
    msg.attach(html_part)

    # Attach flash-report.html
    html_file = ASSETS_DIR.parent / "flash-report.html"
    if html_file.exists():
        attachment = MIMEBase('text', 'html')
        attachment.set_payload(html_file.read_bytes())
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', 'attachment', filename=f"flash-report-{req.bu}-{req.week}.html")
        msg.attach(attachment)

    # Return as downloadable .eml
    from fastapi.responses import Response
    eml_content = msg.as_string()
    return Response(
        content=eml_content,
        media_type="message/rfc822",
        headers={"Content-Disposition": f'attachment; filename="flash-report-{req.bu}-{req.week}.eml"'}
    )


@app.post("/api/report/email-summary")
async def generate_email_summary(req: EmailRequest):
    """AI-generated email summary as a friendly storytelling paragraph"""
    states = load_states()
    entry = states.get(req.week, {}).get(req.bu, {})
    content = entry.get("content", {})
    bu_name = BU_LABELS.get(req.bu, "Brazil Operations")

    # Collect all content
    parts = []
    if content.get("hot_flag"):
        parts.append(f"Hot Flag: {content['hot_flag'].replace('<strong>','').replace('</strong>','')}")
    for i in range(3):
        hl = content.get(f"ev_hl_{i}", "")
        if hl:
            parts.append(f"Positive: {hl}")
    for i in range(3):
        ll = content.get(f"ev_ll_{i}", "")
        if ll:
            parts.append(f"Attention: {ll}")
    for i in range(3):
        hl = content.get(f"bar_hl_{i}", "")
        if hl:
            parts.append(f"Positive: {hl}")
    for i in range(3):
        ll = content.get(f"bar_ll_{i}", "")
        if ll:
            parts.append(f"Attention: {ll}")

    data_text = "\n".join(parts) if parts else "No content saved yet."

    lang_instruction = "Write in English." if req.lang == "EN" else "Write in Brazilian Portuguese."

    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=400,
        messages=[{"role": "user", "content": f"""Write a single friendly paragraph (4-5 sentences, max 80 words) summarizing the safety week for {bu_name} ({req.week}).

Use ONLY the data below. Write as a brief storytelling narrative — easy to read, conversational, like a team update. Start with the overall tone of the week, then mention key wins, then flag any attention points. Use real numbers from the data.

Do NOT use bullet points. Do NOT use headers. Just one fluid paragraph.
{lang_instruction}

DATA:
{data_text}"""}]
    )
    return {"summary": response.content[0].text.strip()}


@app.post("/api/insights")
async def generate_insights(req: InsightsRequest):
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    import json as _json
    goals_file = ASSETS_DIR.parent / "goals.json"
    goals = {}
    bu_goal_key = {"Brazil Operations": "LATAMCF", "Fulfillment Centers": "LATAMCF", "Sort Centers": "ATS-LATAM", "Logistics": "AMZL-LATAM"}.get(req.bu, "LATAMCF")
    if goals_file.exists():
        all_goals = _json.loads(goals_file.read_text())
        goals = all_goals.get(bu_goal_key, {})

    # Map metric labels to goal keys
    METRIC_GOAL_MAP = {
        "Serious Incident Rate": ("SIR", "lower_better"),
        "Recordable Incident Rate": ("RIR", "lower_better"),
        "Lost Time Incident Rate": ("LTIR", "lower_better"),
        "First Aid Rate": ("FAIR", "lower_better"),
        "Dragonfly Rate": (None, "lower_better"),
        "Dragonfly OTC": ("DFY_Closure", "higher_better"),
        "Dragonfly Closure Rate": ("DFY_Closure", "higher_better"),
        "Inspection OTC": ("Inspection_OTC", "higher_better"),
        "Near Miss": (None, "lower_better"),
    }

    # Pre-classify metrics as good or bad using Python logic (not AI)
    highlights_data = []
    lowlights_data = []
    for metric_name, vals in req.metrics.items():
        ytd_str = str(vals.get('ytd','')).replace('%','').replace(',','.')
        try: ytd_val = float(ytd_str)
        except: continue
        week_str = str(vals.get('week','')).replace('%','').replace(',','.')
        try: week_val = float(week_str)
        except: week_val = ytd_val

        goal_key, logic = METRIC_GOAL_MAP.get(metric_name, (None, None))
        if not goal_key or goal_key not in goals: continue
        goal_val = goals[goal_key]["goal"]

        if logic == "lower_better":
            if ytd_val <= goal_val:
                highlights_data.append(f"{metric_name}: YTD={ytd_str} vs Goal={goal_val} (MEETING goal)")
            else:
                lowlights_data.append(f"{metric_name}: YTD={ytd_str} vs Goal={goal_val} (MISSING goal by {((ytd_val-goal_val)/goal_val*100):.0f}%)")
        else:  # higher_better
            if ytd_val >= goal_val:
                highlights_data.append(f"{metric_name}: YTD={ytd_str}% vs Goal={goal_val}% (MEETING goal)")
            else:
                lowlights_data.append(f"{metric_name}: YTD={ytd_str}% vs Goal={goal_val}% (MISSING goal, gap of {(goal_val-ytd_val):.1f}pp)")

    hl_text = "\n".join(f"- {h}" for h in highlights_data) or "- No metrics meeting goal identified"
    ll_text = "\n".join(f"- {l}" for l in lowlights_data) or "- No metrics missing goal identified"

    prompt = f"""Rewrite safety metrics into short factual bullets for Amazon {req.bu} Brazil.

HIGHLIGHTS (metrics that MEET or BEAT goals):
{hl_text}

LOWLIGHTS (metrics that MISS goals):
{ll_text}

STRICT RULES:
1. Each bullet MUST include the metric name, the actual value, and the goal value
2. HIGHLIGHTS: state the fact positively. Example: "SIR: 0.00 YTD vs 0.01 goal — met target"
3. LOWLIGHTS: state the gap clearly. Example: "Dragonfly OTC: 97.6% YTD vs 98% goal — missed by 0.4pp"
4. NEVER say "all metrics within target" or "no action required" if there are lowlights above
5. NEVER add recommendations, opinions, or actions — only state numbers vs goals
6. Max 18 words per bullet
7. If a category has no items, write "No data"

Format exactly:
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


# ── Admin Stats Dashboard ────────────────────────────────────────────────────

@app.get("/api/admin-stats")
def get_admin_stats():
    import csv, os, json
    from datetime import datetime, timezone, timedelta

    DATA_DIR = ASSETS_DIR.parent / "data"
    FLASH_CSV = DATA_DIR / "data-flash-report.csv"

    # --- Report Status ---
    states = load_states()
    # Find current/latest week
    all_weeks = sorted(states.keys(), reverse=True)
    current_week = all_weeks[0] if all_weeks else "—"
    week_data = states.get(current_week, {})
    published = sum(1 for v in week_data.values() if v.get("status") == "published")
    draft = sum(1 for v in week_data.values() if v.get("status") == "draft")
    pending = len(BUS) - published - draft

    report_status = {
        "week": current_week.replace("2026-W", "") if "W" in current_week else current_week,
        "published": published,
        "draft": draft,
        "pending": pending,
        "total_bus": len(BUS),
    }

    # --- Dataset Health ---
    total_hht = 0.0
    sites_count = 0
    missing_sites = 0
    latest_week_num = ""

    if FLASH_CSV.exists():
        try:
            rows = list(csv.DictReader(open(FLASH_CSV, encoding='utf-8-sig')))
            rows2026 = [r for r in rows if r.get('Year') == '2026']
            weeks = sorted(set(r['Week'] for r in rows2026))
            if weeks:
                latest_week_num = weeks[-1]
                week_rows = [r for r in rows2026 if r['Week'] == latest_week_num]
                sites_count = len(week_rows)

                def sf(v):
                    try:
                        return float(str(v).strip().replace(',', '.')) if v and str(v).strip() else 0.0
                    except:
                        return 0.0

                total_hht = sum(sf(r.get('Total_Hours_Week', '0')) for r in week_rows)

                # Missing sites: sites in earlier weeks not present in latest
                all_sites = set(r['Site'] for r in rows2026)
                latest_sites = set(r['Site'] for r in week_rows)
                missing_sites = len(all_sites - latest_sites)
        except:
            pass

    # Dataset freshness
    dataset_files = {
        "data-flash-report": "Flash Report",
        "data-incidents": "Incidents",
        "data-dragonfly": "Dragonfly",
        "data-inspections": "Inspections",
    }
    freshness = []
    now = datetime.now(timezone.utc)
    for key, label in dataset_files.items():
        path = DATA_DIR / f"{key}.csv"
        if path.exists():
            mtime = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)
            age = now - mtime
            age_hours = age.total_seconds() / 3600
            if age_hours < 1:
                age_text = f"{int(age.total_seconds()/60)}min ago"
            elif age_hours < 24:
                age_text = f"{int(age_hours)}h ago"
            else:
                age_text = f"{int(age_hours/24)}d ago"
            freshness.append({"label": label, "age_hours": age_hours, "age_text": age_text})
        else:
            freshness.append({"label": label, "age_hours": 9999, "age_text": "Not uploaded"})

    dataset_health = {
        "total_hht": total_hht,
        "sites_count": sites_count,
        "missing_sites": missing_sites,
        "freshness": freshness,
    }

    # --- Key Metrics (Brazil aggregate for latest week) ---
    key_metrics = {
        "sir": "—", "rir": "—", "ltir": "—", "fair": "—",
        "near_miss": "—", "dfy_rate": "—", "insp_otc": "—", "total_incidents": "—"
    }

    if FLASH_CSV.exists() and latest_week_num:
        try:
            rows = list(csv.DictReader(open(FLASH_CSV, encoding='utf-8-sig')))
            rows2026 = [r for r in rows if r.get('Year') == '2026']
            week_rows = [r for r in rows2026 if r['Week'] == latest_week_num]

            def sf(v):
                try:
                    return float(str(v).strip().replace(',', '.')) if v and str(v).strip() else 0.0
                except:
                    return 0.0

            h_w = sum(sf(r['Total_Hours_Week']) for r in week_rows)
            si_w = sum(sf(r.get('INC_SI_Week', '0')) for r in week_rows)
            ri_w = sum(sf(r.get('INC_RI_Week', '0')) for r in week_rows)
            lti_w = sum(sf(r.get('INC_LTI_Week', '0')) for r in week_rows)
            fai_w = sum(sf(r.get('INC_FAI_Week', '0')) for r in week_rows)
            nm_w = sum(sf(r.get('INC_Near_Miss_Week', '0')) for r in week_rows)
            dfy_w = sum(sf(r.get('DFY_Total_Obs_Week', '0')) for r in week_rows)
            all_inc = sum(sf(r.get('INC_All_Week', '0')) for r in week_rows)

            # Inspection OTC week average
            insp_vals = [sf(r.get('INSP_OTC_Week', '')) for r in week_rows if sf(r.get('INSP_OTC_Week', '')) > 0]
            insp_otc_avg = (sum(insp_vals) / len(insp_vals) * 100) if insp_vals else 0

            def rate(n, h):
                return (n * 200000 / h) if h > 0 else 0

            key_metrics = {
                "sir": f"{rate(si_w, h_w):.2f}",
                "rir": f"{rate(ri_w, h_w):.2f}",
                "ltir": f"{rate(lti_w, h_w):.2f}",
                "fair": f"{rate(fai_w, h_w):.2f}",
                "near_miss": str(int(nm_w)),
                "dfy_rate": f"{rate(dfy_w, h_w):.1f}",
                "insp_otc": f"{insp_otc_avg:.0f}%",
                "total_incidents": str(int(all_inc)),
            }
        except:
            pass

    return {
        "report_status": report_status,
        "dataset_health": dataset_health,
        "key_metrics": key_metrics,
    }


# ── Site Scorecard Table ──────────────────────────────────────────────────────

@app.get("/api/site-scorecard")
def get_site_scorecard(bu: str = ""):
    import csv

    DATA_DIR = ASSETS_DIR.parent / "data"
    FLASH_CSV = DATA_DIR / "data-flash-report.csv"
    if not FLASH_CSV.exists():
        return {"sites": []}

    BU_FILTER_MAP = {'FC': 'LATAMCF', 'SC': 'ATS-LATAM', 'LOG': 'AMZL-LATAM'}

    rows = list(csv.DictReader(open(FLASH_CSV, encoding='utf-8-sig')))
    rows = [r for r in rows if r.get('Year') == '2026']
    weeks = sorted(set(r['Week'] for r in rows))
    if not weeks:
        return {"sites": []}
    latest_week = weeks[-1]
    week_rows = [r for r in rows if r['Week'] == latest_week]

    # Filter by BU if specified
    if bu and bu in BU_FILTER_MAP:
        week_rows = [r for r in week_rows if r.get('BU', '') == BU_FILTER_MAP[bu]]

    BU_MAP = {'LATAMCF': 'FC', 'ATS-LATAM': 'SC', 'AMZL-LATAM': 'LOG'}
    GOALS = {
        'LATAMCF': {'sir': 0.01, 'rir': 0.01, 'ltir': 34.15, 'fair': 20.69, 'insp_otc': 98, 'act_otc': 98, 'dfy_closure': 98},
        'ATS-LATAM': {'sir': 0.03, 'rir': 0.03, 'ltir': 50.51, 'fair': 30.00, 'insp_otc': 98, 'act_otc': 98, 'dfy_closure': 98},
        'AMZL-LATAM': {'sir': 0.14, 'rir': 0.14, 'ltir': 11.20, 'fair': 11.75, 'insp_otc': 98, 'act_otc': 98, 'dfy_closure': 98},
    }

    def sf(v):
        try: return float(str(v).strip().replace(',', '.')) if v and str(v).strip() else 0.0
        except: return 0.0

    def rate(n, h): return (n * 200000 / h) if h > 0 else 0

    sites = []
    for r in sorted(week_rows, key=lambda x: (-sf(x.get('Total_Hours_Week', '0')), x.get('Site', ''))):
        bu = r.get('BU', '')
        h_w = sf(r.get('Total_Hours_Week', ''))
        goals = GOALS.get(bu, {})

        sir_w = rate(sf(r.get('INC_SI_Week', '')), h_w)
        rir_w = rate(sf(r.get('INC_RI_Week', '')), h_w)
        ltir_w = rate(sf(r.get('INC_LTI_Week', '')), h_w)
        fair_w = rate(sf(r.get('INC_FAI_Week', '')), h_w)
        nm_w = int(sf(r.get('INC_Near_Miss_Week', '')))
        dfy_w = int(sf(r.get('DFY_Total_Obs_Week', '')))

        def status(val, goal, lower=True):
            if goal is None: return 'na'
            if lower:
                if val <= goal: return 'met'
                if val <= goal * 1.5: return 'close'
                return 'miss'
            else:
                if val >= goal: return 'met'
                if val >= goal * 0.5: return 'close'
                return 'miss'

        # Barriers metrics
        insp_otc_raw = sf(r.get('INSP_Inspection_OTC', ''))
        insp_otc_val = insp_otc_raw * 100 if insp_otc_raw <= 1 else insp_otc_raw
        act_otc_raw = sf(r.get('INSP_Task_OTC', ''))
        act_otc_val = act_otc_raw * 100 if act_otc_raw <= 1 else act_otc_raw
        dfy_otc_raw = sf(r.get('DFY_Closure_Rate_YTD', ''))
        dfy_otc_val = dfy_otc_raw * 100 if dfy_otc_raw <= 1 else dfy_otc_raw

        sites.append({
            'site': r.get('Site', ''),
            'bu': BU_MAP.get(bu, bu),
            'hht': int(h_w),
            'lat': sf(r.get('Latitude', '')),
            'lng': sf(r.get('Longitude', '')),
            'sir': {'val': round(sir_w, 2), 'status': status(sir_w, goals.get('sir'), True)},
            'rir': {'val': round(rir_w, 2), 'status': status(rir_w, goals.get('rir'), True)},
            'ltir': {'val': round(ltir_w, 2), 'status': status(ltir_w, goals.get('ltir'), True)},
            'fair': {'val': round(fair_w, 2), 'status': status(fair_w, goals.get('fair'), True)},
            'nm': nm_w,
            'dfy': dfy_w,
            'insp_otc': {'val': round(insp_otc_val, 1), 'status': status(insp_otc_val, goals.get('insp_otc'), lower=False)},
            'act_otc': {'val': round(act_otc_val, 1), 'status': status(act_otc_val, goals.get('act_otc'), lower=False)},
            'dfy_otc': {'val': round(dfy_otc_val, 1), 'status': status(dfy_otc_val, goals.get('dfy_closure'), lower=False)},
        })

    return {"sites": sites, "week": latest_week}


# ── Heatmap Data ──────────────────────────────────────────────────────────────

@app.get("/api/heatmap")
def get_heatmap(bu: str = ""):
    import csv
    from datetime import datetime as dt, timedelta

    BU_FILTER_MAP = {'FC': 'LATAMCF', 'SC': 'ATS-LATAM', 'LOG': 'AMZL-LATAM'}
    bu_filter = BU_FILTER_MAP.get(bu) if bu else None

    DATA_DIR = ASSETS_DIR.parent / "data"

    # Dynamic week range
    now = dt.now()
    day = now.weekday()
    last_sun = now if day == 6 else now - timedelta(days=(day + 1))
    last_mon = last_sun - timedelta(days=6)
    W_START = last_mon.strftime('%Y-%m-%d')
    W_END = last_sun.strftime('%Y-%m-%d')

    # Get site coordinates from flash-report CSV
    FLASH_CSV = DATA_DIR / "data-flash-report.csv"
    site_coords = {}
    if FLASH_CSV.exists():
        rows = list(csv.DictReader(open(FLASH_CSV, encoding='utf-8-sig')))
        for r in rows:
            site = r.get('Site', '')
            try:
                lat = float(r.get('Latitude', '0').replace(',', '.'))
                lng = float(r.get('Longitude', '0').replace(',', '.'))
                if lat != 0 and lng != 0:
                    site_coords[site] = (lat, lng)
            except:
                pass

    # Severity weights
    NM_SEV_WEIGHT = {'A': 10, 'B': 7, 'C': 4, 'D': 1, 'PENDING': 1}
    DFY_SEV_WEIGHT = {'5': 10, '4': 7, '3': 4, '2': 2, '1': 1}

    points = []

    # From nearmiss/incidents (individual events with severity)
    NM_FILE = DATA_DIR / "data-nearmiss.csv"
    if NM_FILE.exists():
        nm = list(csv.DictReader(open(NM_FILE, encoding='utf-8-sig')))
        for r in nm:
            if W_START <= r.get('Incident Date', '')[:10] <= W_END:
                if bu_filter and r.get('OBR BU', '').strip() != bu_filter:
                    continue
                site = r.get('Site', '')
                if site in site_coords:
                    lat, lng = site_coords[site]
                    sev = r.get('Severity', '').strip()
                    weight = NM_SEV_WEIGHT.get(sev, 1)
                    # Add slight random offset to avoid stacking
                    import random
                    lat += random.uniform(-0.02, 0.02)
                    lng += random.uniform(-0.02, 0.02)
                    points.append([lat, lng, weight])

    # From dragonfly (safety observations with AI severity)
    DFY_FILE = DATA_DIR / "data-dragonfly.csv"
    if DFY_FILE.exists():
        dfy = list(csv.DictReader(open(DFY_FILE, encoding='utf-8-sig')))
        for r in dfy:
            if W_START <= r.get('Finding Creation Timestamp (UTC)', '')[:10] <= W_END:
                if bu_filter and r.get('OBR BU', '').strip() != bu_filter:
                    continue
                site = r.get('Site', '')
                if site in site_coords:
                    lat, lng = site_coords[site]
                    sev = r.get('Severity (AI)', '').strip()
                    weight = DFY_SEV_WEIGHT.get(sev, 0)
                    if weight > 0:
                        import random
                        lat += random.uniform(-0.03, 0.03)
                        lng += random.uniform(-0.03, 0.03)
                        points.append([lat, lng, weight])

    return {"points": points, "total": len(points), "week_start": W_START, "week_end": W_END}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3003)


