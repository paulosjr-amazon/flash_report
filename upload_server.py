#!/usr/bin/env python3
from pathlib import Path
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

ASSETS_DIR = Path("/home/paulosjr/.workspace/flash_report/assets")
ICONS_DIR = ASSETS_DIR / "icons"
ICONS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = {"image/png", "image/jpeg", "image/svg+xml", "image/webp"}

SLOTS = {
    "header-logo":          ("assets", "🛡️ Logo Header (esq.)"),
    "safetogo-logo":        ("assets", "✅ Safe to Go"),
    "amazon-logo":          ("assets", "📦 Amazon"),
    "footer-logo":          ("assets", "🦶 Logo Rodapé"),
    "icon-did-you-know":    ("icons",  "💡 Did You Know?"),
    "icon-success-stories": ("icons",  "🏆 Success Stories"),
    "icon-hot-flag":        ("icons",  "🚩 Hot Flag"),
    "icon-best-dragonfly":  ("icons",  "🐉 Best Dragonfly"),
}

HTML = """<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Upload Assets — Flash Report</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Inter',system-ui,sans-serif;background:#f2f2f2;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:2rem}
  .card{background:#fff;border-radius:20px;box-shadow:0 2px 20px rgba(0,0,0,.07);padding:2.5rem;width:100%;max-width:500px}
  h2{font-size:1.05rem;font-weight:700;color:#1a1a1a;margin-bottom:.25rem}
  p{font-size:.8rem;color:#888;margin-bottom:1.25rem}
  .section-label{font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#aaa;margin-bottom:.5rem;margin-top:1rem}
  .slots{display:grid;grid-template-columns:1fr 1fr;gap:.5rem;margin-bottom:.25rem}
  .slot{padding:.55rem .8rem;border:2px solid #e0e0e0;border-radius:10px;cursor:pointer;font-size:.78rem;font-weight:600;color:#555;background:#fafafa;transition:.15s}
  .slot:hover{border-color:#A8D872;background:#f4faf0}
  .slot.active{border-color:#1c6b3a;background:linear-gradient(90deg,#A8D872,#B7DCCB);color:#1c3d12}
  .drop{border:2px dashed #d4e8d5;border-radius:12px;padding:1.5rem;text-align:center;cursor:pointer;margin:1rem 0;transition:.15s}
  .drop:hover{background:#f4faf0}
  .drop input{display:none}
  .drop-label{font-size:.85rem;color:#4CAF50;font-weight:600}
  .drop-hint{font-size:.72rem;color:#aaa;margin-top:.3rem}
  img#preview{display:none;max-height:70px;max-width:200px;margin:.75rem auto;border-radius:8px;display:block}
  button{width:100%;padding:.65rem;background:#1c6b3a;color:#fff;border:none;border-radius:999px;font-weight:700;font-size:.9rem;cursor:pointer}
  button:disabled{opacity:.4;cursor:not-allowed}
  .msg{margin-top:.9rem;padding:.6rem 1rem;border-radius:8px;font-size:.82rem;display:none}
  .msg.ok{display:block;background:#edf5ee;color:#1c6b3a}
  .msg.err{display:block;background:#fde8e8;color:#c62828}
</style>
</head>
<body>
<div class="card">
  <h2>Upload de Assets</h2>
  <p>Selecione o slot e o arquivo. PNG, JPG, SVG ou WEBP.</p>

  <div class="section-label">Logos do Header</div>
  <div class="slots">
    <div class="slot active" data-slot="header-logo" onclick="setSlot(this)">🛡️ Logo Header</div>
    <div class="slot" data-slot="safetogo-logo" onclick="setSlot(this)">✅ Safe to Go</div>
    <div class="slot" data-slot="amazon-logo" onclick="setSlot(this)">📦 Amazon</div>
    <div class="slot" data-slot="footer-logo" onclick="setSlot(this)">🦶 Logo Rodapé</div>
  </div>

  <div class="section-label">Ícones dos Cards</div>
  <div class="slots">
    <div class="slot" data-slot="icon-did-you-know" onclick="setSlot(this)">💡 Did You Know?</div>
    <div class="slot" data-slot="icon-success-stories" onclick="setSlot(this)">🏆 Success Stories</div>
    <div class="slot" data-slot="icon-hot-flag" onclick="setSlot(this)">🚩 Hot Flag</div>
    <div class="slot" data-slot="icon-best-dragonfly" onclick="setSlot(this)">🐉 Best Dragonfly</div>
  </div>

  <div class="drop" onclick="document.getElementById('f').click()">
    <input type="file" id="f" accept=".png,.jpg,.jpeg,.svg,.webp" onchange="onFile(this)">
    <div class="drop-label">Clique para selecionar</div>
    <div class="drop-hint">PNG · JPG · SVG · WEBP</div>
  </div>
  <img id="preview" alt="preview">
  <button id="btn" onclick="upload()" disabled>Fazer Upload</button>
  <div class="msg" id="msg"></div>
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
    dest_dir = ICONS_DIR if SLOTS[slot][0] == "icons" else ASSETS_DIR
    suffix = Path(file.filename).suffix or ".png"
    for old in dest_dir.glob(f"{slot}.*"):
        old.unlink()
    dest = dest_dir / f"{slot}{suffix}"
    dest.write_bytes(await file.read())
    return {"status": "ok", "filename": dest.name}

app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3003)
