"""
OKF Knowledge Graph Visualizer.
Parsea el bundle memoria/ y genera un HTML self-contained con grafo de fuerza.
"""
import json
import re
from pathlib import Path

BUNDLE_ROOTS = [
    Path("memoria"),
    Path("core_agent/tasks"),
]

RESERVED = {"index.md", "log.md"}

TYPE_COLORS = {
    "metric_domain": "#3B82F6",
    "client_profile": "#00D4FF",
    "task_recipe": "#8B5CF6",
}

TYPE_LABELS = {
    "metric_domain": "Dominio Analítico",
    "client_profile": "Perfil de Cliente",
    "task_recipe": "Receta del Harness",
}


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extrae el bloque YAML frontmatter y retorna (dict, body)."""
    if not content.startswith("---"):
        return {}, content
    end = content.find("\n---", 3)
    if end == -1:
        return {}, content
    fm_text = content[3:end]
    body = content[end + 4:]

    # Intentar con PyYAML (disponible como dep transitiva de Pandera)
    try:
        import yaml
        fm = yaml.safe_load(fm_text) or {}
        return fm, body
    except Exception:
        pass

    # Fallback: parser manual para frontmatter simple
    fm: dict = {}
    for line in fm_text.splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip().strip('"')
        if val.startswith("[") and val.endswith("]"):
            val = [v.strip() for v in val[1:-1].split(",")]
        fm[key] = val
    return fm, body


def _extract_links(body: str, source_path: Path) -> list[str]:
    """Resuelve links relativos .md del body a rutas absolutas."""
    targets = []
    for m in re.finditer(r'\[([^\]]+)\]\(([^)]+\.md)\)', body):
        href = m.group(2)
        if href.startswith("http"):
            continue
        resolved = (source_path.parent / href).resolve()
        targets.append(str(resolved))
    return targets


def build_graph() -> dict:
    """Parsea el bundle OKF y retorna {nodes, edges}."""
    nodes: dict[str, dict] = {}
    raw_edges: list[tuple[str, str]] = []

    for root in BUNDLE_ROOTS:
        if not root.exists():
            continue
        for md_file in sorted(root.rglob("*.md")):
            if md_file.name in RESERVED:
                continue
            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception:
                continue

            fm, body = _parse_frontmatter(content)
            node_type = str(fm.get("type", "")).strip()
            if not node_type:
                continue

            tags = fm.get("tags", [])
            if not isinstance(tags, list):
                tags = []

            node_id = str(md_file.resolve())
            nodes[node_id] = {
                "id": node_id,
                "type": node_type,
                "title": str(fm.get("title", md_file.stem)).strip('"'),
                "description": str(fm.get("description", "")).strip('"'),
                "resource": str(fm.get("resource", "")).strip('"'),
                "tags": tags,
                "timestamp": str(fm.get("timestamp", "")),
                "file": "/".join(md_file.parts[-2:]),
                "color": TYPE_COLORS.get(node_type, "#94A3B8"),
                "typeLabel": TYPE_LABELS.get(node_type, node_type),
            }

            for tgt in _extract_links(body, md_file):
                raw_edges.append((node_id, tgt))

    edges = [
        {"source": src, "target": tgt}
        for src, tgt in raw_edges
        if src in nodes and tgt in nodes
    ]

    return {"nodes": list(nodes.values()), "edges": edges}


_HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MalayAI — Grafo OKF</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#050810;color:#E2E8F0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;display:flex;height:100vh;overflow:hidden}
#cv-wrap{flex:1;position:relative;min-width:0}
canvas{display:block;cursor:default}
#panel{width:320px;min-width:320px;background:#0D1525;border-left:1px solid #1E293B;display:flex;flex-direction:column;overflow:hidden}
#ph{padding:20px;border-bottom:1px solid #1E293B}
#ph small{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#475569;display:block;margin-bottom:4px}
#ph .brand{font-size:1rem;font-weight:600;background:linear-gradient(90deg,#3B82F6,#00D4FF);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
#pb{flex:1;padding:20px;overflow-y:auto}
.placeholder{color:#475569;font-size:.85rem;margin-top:48px;text-align:center;line-height:1.7}
.badge{display:inline-block;padding:2px 10px;border-radius:999px;font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.8px;margin-bottom:12px}
.ntitle{font-size:.95rem;font-weight:600;color:#F1F5F9;margin-bottom:8px;line-height:1.4}
.ndesc{font-size:.8rem;color:#94A3B8;line-height:1.6;margin-bottom:14px}
.dlabel{font-size:.62rem;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:#475569;margin-bottom:4px;margin-top:14px}
.dval{font-size:.78rem;color:#CBD5E1;font-family:"SF Mono","Fira Code",monospace;word-break:break-all;background:#050810;padding:6px 10px;border-radius:6px;border:1px solid #1E293B}
.tags{display:flex;flex-wrap:wrap;gap:5px;margin-top:4px}
.tag{padding:2px 8px;border-radius:4px;font-size:.68rem;background:#1E293B;color:#94A3B8}
#stats{padding:0 20px 12px;font-size:.7rem;color:#475569}
#legend{padding:14px 20px;border-top:1px solid #1E293B}
#legend .lt{font-size:.62rem;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:#475569;margin-bottom:10px}
.li{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.ld{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.lx{font-size:.75rem;color:#94A3B8}
</style>
</head>
<body>
<div id="cv-wrap"><canvas id="g"></canvas></div>
<div id="panel">
  <div id="ph">
    <small>MalayAI Lab</small>
    <div class="brand">Grafo de Conocimiento OKF</div>
  </div>
  <div id="pb"><div class="placeholder">Haz clic en un nodo<br>para ver sus detalles</div></div>
  <div id="stats"></div>
  <div id="legend">
    <div class="lt">Tipos de nodo</div>
    <div class="li"><div class="ld" style="background:#3B82F6"></div><span class="lx">metric_domain — KPIs y esquema</span></div>
    <div class="li"><div class="ld" style="background:#00D4FF"></div><span class="lx">client_profile — Perfil de cliente</span></div>
    <div class="li"><div class="ld" style="background:#8B5CF6"></div><span class="lx">task_recipe — Receta del harness</span></div>
  </div>
</div>
<script>
const DATA = __GRAPH_DATA__;
const canvas = document.getElementById('g');
const ctx = canvas.getContext('2d');
const pb = document.getElementById('pb');
const statsEl = document.getElementById('stats');
const wrap = document.getElementById('cv-wrap');
let dpr = devicePixelRatio || 1;
let W, H;

function resize() {
  W = wrap.clientWidth; H = wrap.clientHeight;
  canvas.width = W * dpr; canvas.height = H * dpr;
  canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
  ctx.scale(dpr, dpr);
}

// Build simulation nodes
const nodes = DATA.nodes.map(n => ({ ...n, x: 0, y: 0, vx: 0, vy: 0, r: 18 }));
const nmap = {};
nodes.forEach(n => nmap[n.id] = n);
const edges = DATA.edges.map(e => ({ s: nmap[e.source], t: nmap[e.target] })).filter(e => e.s && e.t);

function scatter() {
  nodes.forEach((n, i) => {
    const a = (i / nodes.length) * Math.PI * 2;
    const rad = Math.min(W, H) * 0.28;
    n.x = W/2 + Math.cos(a)*rad + (Math.random()-.5)*60;
    n.y = H/2 + Math.sin(a)*rad + (Math.random()-.5)*60;
  });
}

let selected = null, hovered = null, dragging = null;
let tick = 0, running = true;

function sim() {
  if (!running) return;
  const REP=5000, SK=0.06, SL=150, DAMP=0.72, GX=0.025;
  for (let i=0;i<nodes.length;i++) {
    for (let j=i+1;j<nodes.length;j++) {
      const a=nodes[i],b=nodes[j];
      let dx=b.x-a.x, dy=b.y-a.y, d=Math.sqrt(dx*dx+dy*dy)||1;
      const f=REP/(d*d);
      const fx=(dx/d)*f, fy=(dy/d)*f;
      a.vx-=fx;a.vy-=fy;b.vx+=fx;b.vy+=fy;
    }
  }
  edges.forEach(e=>{
    let dx=e.t.x-e.s.x,dy=e.t.y-e.s.y,d=Math.sqrt(dx*dx+dy*dy)||1;
    const f=(d-SL)*SK;
    const fx=(dx/d)*f,fy=(dy/d)*f;
    e.s.vx+=fx;e.s.vy+=fy;e.t.vx-=fx;e.t.vy-=fy;
  });
  nodes.forEach(n=>{
    n.vx+=(W/2-n.x)*GX; n.vy+=(H/2-n.y)*GX;
    n.vx*=DAMP; n.vy*=DAMP;
    n.x+=n.vx; n.y+=n.vy;
    n.x=Math.max(n.r+16,Math.min(W-n.r-16,n.x));
    n.y=Math.max(n.r+16,Math.min(H-n.r-16,n.y));
  });
  if(++tick>350) running=false;
}

function shortLabel(n) {
  let t = n.title;
  if (t.includes(': ')) return t.split(': ').pop();
  return t.replace(/^(Métricas de |Receta: )/, '');
}

function isAdj(n) {
  return selected && edges.some(e=>(e.s===selected&&e.t===n)||(e.t===selected&&e.s===n));
}

function draw() {
  ctx.clearRect(0,0,W,H);

  // Edges
  edges.forEach(e=>{
    const hi = selected && (e.s===selected||e.t===selected);
    ctx.beginPath();
    ctx.moveTo(e.s.x,e.s.y); ctx.lineTo(e.t.x,e.t.y);
    ctx.strokeStyle = hi ? '#3B82F6' : '#1E293B';
    ctx.lineWidth = hi ? 2 : 1;
    ctx.stroke();
    if (hi) {
      const dx=e.t.x-e.s.x, dy=e.t.y-e.s.y, d=Math.sqrt(dx*dx+dy*dy)||1;
      const ang=Math.atan2(dy,dx), al=9;
      const tx=e.t.x-(dx/d)*(e.t.r+3), ty=e.t.y-(dy/d)*(e.t.r+3);
      ctx.beginPath();
      ctx.moveTo(tx,ty);
      ctx.lineTo(tx-al*Math.cos(ang-.4),ty-al*Math.sin(ang-.4));
      ctx.lineTo(tx-al*Math.cos(ang+.4),ty-al*Math.sin(ang+.4));
      ctx.closePath(); ctx.fillStyle='#3B82F6'; ctx.fill();
    }
  });

  // Nodes
  nodes.forEach(n=>{
    const sel=n===selected, hov=n===hovered, adj=isAdj(n);
    // Glow
    if (sel||adj) {
      const gr=ctx.createRadialGradient(n.x,n.y,n.r,n.x,n.y,n.r+10);
      gr.addColorStop(0,n.color+'55'); gr.addColorStop(1,'transparent');
      ctx.beginPath(); ctx.arc(n.x,n.y,n.r+10,0,Math.PI*2);
      ctx.fillStyle=gr; ctx.fill();
    }
    // Circle
    ctx.beginPath(); ctx.arc(n.x,n.y,n.r,0,Math.PI*2);
    ctx.fillStyle = sel ? n.color : (adj ? n.color+'BB' : n.color+'44');
    ctx.fill();
    ctx.strokeStyle=n.color; ctx.lineWidth=sel?2.5:hov?2:1.5; ctx.stroke();
    // Icon center
    ctx.fillStyle = sel ? '#fff' : n.color;
    ctx.font=`bold 13px sans-serif`;
    ctx.textAlign='center'; ctx.textBaseline='middle';
    const icon = n.type==='metric_domain'?'◈':n.type==='client_profile'?'◎':'⬡';
    ctx.fillText(icon,n.x,n.y);
    // Label below
    ctx.fillStyle=sel?'#F1F5F9':'#64748B';
    ctx.font=`${sel?600:400} 10.5px -apple-system,sans-serif`;
    ctx.textBaseline='top';
    ctx.fillText(shortLabel(n),n.x,n.y+n.r+4);
  });
}

function loop() { sim(); draw(); requestAnimationFrame(loop); }

function hitTest(mx,my) {
  for(const n of nodes){const dx=n.x-mx,dy=n.y-my;if(dx*dx+dy*dy<=n.r*n.r)return n;}return null;
}

canvas.addEventListener('mousemove',e=>{
  const r=canvas.getBoundingClientRect();
  hovered=hitTest(e.clientX-r.left,e.clientY-r.top);
  canvas.style.cursor=hovered?'pointer':'default';
});

canvas.addEventListener('mousedown',e=>{
  const r=canvas.getBoundingClientRect();
  dragging=hitTest(e.clientX-r.left,e.clientY-r.top);
  if(dragging) running=false;
});
canvas.addEventListener('mousemove',e=>{
  if(!dragging)return;
  const r=canvas.getBoundingClientRect();
  dragging.x=e.clientX-r.left; dragging.y=e.clientY-r.top;
  dragging.vx=0; dragging.vy=0;
},{passive:true});
canvas.addEventListener('mouseup',()=>{dragging=null});

canvas.addEventListener('click',e=>{
  const r=canvas.getBoundingClientRect();
  const n=hitTest(e.clientX-r.left,e.clientY-r.top);
  selected=(n===selected)?null:n;
  renderPanel(selected);
});

function renderPanel(n) {
  if (!n) { pb.innerHTML='<div class="placeholder">Haz clic en un nodo<br>para ver sus detalles</div>'; return; }
  const tagsHtml = n.tags.length
    ? `<div class="dlabel">Etiquetas</div><div class="tags">${n.tags.map(t=>`<span class="tag">${t}</span>`).join('')}</div>`:'';
  pb.innerHTML=`
    <span class="badge" style="background:${n.color}20;color:${n.color};border:1px solid ${n.color}40">${n.typeLabel}</span>
    <div class="ntitle">${n.title}</div>
    <div class="ndesc">${n.description||'Sin descripción.'}</div>
    ${n.resource?`<div class="dlabel">Recurso</div><div class="dval">${n.resource}</div>`:''}
    ${tagsHtml}
    ${n.timestamp?`<div class="dlabel">Timestamp</div><div class="dval">${n.timestamp}</div>`:''}
    <div class="dlabel">Archivo</div><div class="dval">${n.file}</div>
  `;
}

statsEl.textContent = `${nodes.length} nodos · ${edges.length} vínculos`;

window.addEventListener('resize',()=>{ resize(); scatter(); running=true; tick=0; });
resize(); scatter(); loop();
</script>
</body>
</html>"""


def generate(output_path: Path = Path("memoria/grafo.html")) -> Path:
    """Construye el grafo OKF y escribe el HTML visualizador."""
    graph = build_graph()
    graph_json = json.dumps(graph, ensure_ascii=False, separators=(",", ":"))
    html = _HTML.replace("__GRAPH_DATA__", graph_json)
    output_path.write_text(html, encoding="utf-8")
    return output_path.resolve()