"""
HTML Dashboard Generator - Interactief Vastgoedmarkt Dashboard
"""

import json
from datetime import datetime


def generate_dashboard(data, output_path="vastgoed_dashboard.html"):
    week = datetime.now().strftime("Week %W — %d %B %Y")
    gegenereerd = datetime.now().strftime("%d/%m/%Y om %H:%M")

    # Statistieken berekenen
    provincies = ["Antwerpen", "Vlaams-Brabant", "Limburg"]
    types = ["Woning", "Appartement", "Klein (<50m²)"]
    btw_regimes = ["Nieuwbouw 21% BTW", "Nieuwbouw 6% BTW", "Bestaand (reg. rechten)"]

    def gem_pm2(subset):
        vals = [r["prijs_per_m2"] for r in subset if r.get("prijs_per_m2")]
        return round(sum(vals) / len(vals)) if vals else 0

    # Data voor charts
    chart_data = {
        "provincies": provincies,
        "per_prov_type": {
            t: [gem_pm2([r for r in data if r["provincie"] == p and r["type"] == t])
                for p in provincies]
            for t in types
        },
        "per_prov_btw": {
            btw: [gem_pm2([r for r in data if r["provincie"] == p and r["btw_regime"] == btw])
                  for p in provincies]
            for btw in btw_regimes
        },
        "totaal_per_prov": [len([r for r in data if r["provincie"] == p]) for p in provincies],
    }

    # Top listings (duurste per m²)
    top_listings = sorted(
        [r for r in data if r.get("prijs_per_m2")],
        key=lambda x: x["prijs_per_m2"],
        reverse=True
    )[:50]

    # KPI's
    total = len(data)
    gem_all = gem_pm2(data)
    gem_nw  = gem_pm2([r for r in data if "Nieuwbouw" in r.get("btw_regime", "")])
    gem_best = gem_pm2([r for r in data if r.get("btw_regime") == "Bestaand (reg. rechten)"])
    n_nieuwbouw = len([r for r in data if "Nieuwbouw" in r.get("btw_regime", "")])
    pct_nw = round(n_nieuwbouw / total * 100, 1) if total else 0

    listings_json = json.dumps(top_listings, ensure_ascii=False)
    chart_json    = json.dumps(chart_data, ensure_ascii=False)
    all_data_json = json.dumps(data, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vastgoedmarkt Dashboard — {week}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
<style>
  :root {{
    --dark:    #1B3A5C;
    --mid:     #2E6DA4;
    --light:   #D6E4F0;
    --accent:  #E8A020;
    --green:   #217346;
    --orange:  #C55A11;
    --purple:  #5B2D8E;
    --gray:    #F5F7FA;
    --border:  #DDE3EC;
    --text:    #2C3E50;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: var(--gray); color: var(--text); }}

  /* ── Header ── */
  .header {{
    background: linear-gradient(135deg, var(--dark) 0%, var(--mid) 100%);
    color: white; padding: 24px 36px; display: flex; justify-content: space-between;
    align-items: center; box-shadow: 0 4px 16px rgba(0,0,0,.25);
  }}
  .header h1 {{ font-size: 1.8rem; font-weight: 700; letter-spacing: -.5px; }}
  .header .meta {{ font-size: .85rem; opacity: .85; margin-top: 4px; }}
  .badge {{ background: var(--accent); color: white; padding: 4px 12px;
            border-radius: 20px; font-size: .8rem; font-weight: 600; }}

  /* ── KPI's ── */
  .kpi-row {{ display: grid; grid-template-columns: repeat(4, 1fr);
              gap: 16px; padding: 24px 36px 8px; }}
  .kpi {{ background: white; border-radius: 12px; padding: 20px 24px;
          border-top: 4px solid var(--mid); box-shadow: 0 2px 8px rgba(0,0,0,.07); }}
  .kpi .label {{ font-size: .8rem; text-transform: uppercase; letter-spacing: .5px;
                 color: #6B7C93; font-weight: 600; margin-bottom: 6px; }}
  .kpi .value {{ font-size: 2rem; font-weight: 700; color: var(--dark); }}
  .kpi .sub   {{ font-size: .8rem; color: #888; margin-top: 4px; }}
  .kpi.green  {{ border-color: var(--green); }}
  .kpi.orange {{ border-color: var(--orange); }}
  .kpi.purple {{ border-color: var(--purple); }}

  /* ── Charts ── */
  .charts {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px;
             padding: 16px 36px; }}
  .chart-card {{ background: white; border-radius: 12px; padding: 24px;
                 box-shadow: 0 2px 8px rgba(0,0,0,.07); }}
  .chart-card h3 {{ font-size: 1rem; color: var(--dark); margin-bottom: 16px;
                    font-weight: 600; border-bottom: 2px solid var(--light);
                    padding-bottom: 8px; }}
  .chart-container {{ position: relative; height: 260px; }}

  /* ── Tabel ── */
  .table-section {{ padding: 0 36px 36px; }}
  .table-header {{ display: flex; justify-content: space-between; align-items: center;
                   margin-bottom: 16px; }}
  .table-header h2 {{ font-size: 1.2rem; color: var(--dark); font-weight: 700; }}
  .controls {{ display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }}
  .controls select, .controls input {{
    padding: 8px 14px; border: 1.5px solid var(--border); border-radius: 8px;
    font-size: .9rem; background: white; color: var(--text); outline: none;
    transition: border .2s;
  }}
  .controls select:focus, .controls input:focus {{ border-color: var(--mid); }}
  .controls label {{ font-size: .85rem; color: #666; font-weight: 600; }}

  table {{ width: 100%; border-collapse: separate; border-spacing: 0;
           background: white; border-radius: 12px; overflow: hidden;
           box-shadow: 0 2px 8px rgba(0,0,0,.07); }}
  thead tr {{ background: var(--dark); color: white; }}
  thead th {{ padding: 14px 12px; text-align: left; font-size: .8rem;
              text-transform: uppercase; letter-spacing: .4px; font-weight: 600;
              cursor: pointer; user-select: none; white-space: nowrap; }}
  thead th:hover {{ background: var(--mid); }}
  thead th.sorted-asc::after  {{ content: " ▲"; font-size: .7rem; }}
  thead th.sorted-desc::after {{ content: " ▼"; font-size: .7rem; }}

  tbody tr {{ transition: background .15s; }}
  tbody tr:hover {{ background: var(--light) !important; }}
  tbody tr:nth-child(even) {{ background: #FAFBFD; }}
  td {{ padding: 11px 12px; font-size: .88rem; border-bottom: 1px solid var(--border); }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}

  .badge-btw {{ padding: 3px 10px; border-radius: 12px; font-size: .75rem;
               font-weight: 600; white-space: nowrap; }}
  .btw-21  {{ background: #FCE4D6; color: #C55A11; }}
  .btw-6   {{ background: #E2EFDA; color: #217346; }}
  .btw-reg {{ background: #EAE0F5; color: #5B2D8E; }}

  .badge-type {{ padding: 3px 10px; border-radius: 12px; font-size: .75rem;
                font-weight: 600; }}
  .type-w {{ background: #D6E4F0; color: #1B3A5C; }}
  .type-a {{ background: #FFF2CC; color: #7F6000; }}
  .type-k {{ background: #FFE0CC; color: #843C0C; }}

  .pagination {{ display: flex; justify-content: center; align-items: center;
                 gap: 8px; padding: 20px 0; }}
  .pagination button {{
    padding: 8px 16px; border: 1.5px solid var(--border); background: white;
    border-radius: 8px; cursor: pointer; font-size: .9rem; transition: all .2s;
  }}
  .pagination button:hover {{ background: var(--light); border-color: var(--mid); }}
  .pagination button.active {{ background: var(--mid); color: white; border-color: var(--mid); }}
  .page-info {{ font-size: .85rem; color: #666; }}

  /* ── Footer ── */
  footer {{ text-align: center; padding: 20px; color: #999; font-size: .8rem;
            border-top: 1px solid var(--border); margin-top: 8px; }}

  @media (max-width: 900px) {{
    .kpi-row {{ grid-template-columns: 1fr 1fr; }}
    .charts   {{ grid-template-columns: 1fr; }}
    .kpi-row, .charts, .table-section {{ padding-left: 16px; padding-right: 16px; }}
    .header {{ flex-direction: column; gap: 12px; text-align: center; }}
  }}
</style>
</head>
<body>

<div class="header">
  <div>
    <h1>🏠 Vastgoedmarkt Dashboard</h1>
    <div class="meta">Antwerpen · Vlaams-Brabant · Limburg &nbsp;|&nbsp; {week}</div>
    <div class="meta" style="margin-top:4px">Gegenereerd op {gegenereerd}</div>
  </div>
  <span class="badge">{total} listings</span>
</div>

<!-- KPI's -->
<div class="kpi-row">
  <div class="kpi">
    <div class="label">Gem. Prijs/m² (alle)</div>
    <div class="value">{gem_all:,} €</div>
    <div class="sub">Gemiddelde over alle types & provincies</div>
  </div>
  <div class="kpi green">
    <div class="label">Gem. Prijs/m² Nieuwbouw</div>
    <div class="value">{gem_nw:,} €</div>
    <div class="sub">6% &amp; 21% BTW gecombineerd</div>
  </div>
  <div class="kpi orange">
    <div class="label">Gem. Prijs/m² Bestaand</div>
    <div class="value">{gem_best:,} €</div>
    <div class="sub">Registratierechten van toepassing</div>
  </div>
  <div class="kpi purple">
    <div class="label">Aandeel Nieuwbouw</div>
    <div class="value">{pct_nw}%</div>
    <div class="sub">Van {n_nieuwbouw} op {total} listings</div>
  </div>
</div>

<!-- Charts -->
<div class="charts">
  <div class="chart-card">
    <h3>📍 Gem. Prijs/m² per Provincie & Type</h3>
    <div class="chart-container"><canvas id="chartProvType"></canvas></div>
  </div>
  <div class="chart-card">
    <h3>🏗️ Gem. Prijs/m² per BTW-Regime & Provincie</h3>
    <div class="chart-container"><canvas id="chartBTW"></canvas></div>
  </div>
</div>

<!-- Datatable -->
<div class="table-section">
  <div class="table-header">
    <h2>📋 Alle Listings</h2>
    <div class="controls">
      <label>Provincie:</label>
      <select id="filterProv">
        <option value="">Alle provincies</option>
        <option>Antwerpen</option>
        <option>Vlaams-Brabant</option>
        <option>Limburg</option>
      </select>
      <label>Type:</label>
      <select id="filterType">
        <option value="">Alle types</option>
        <option>Woning</option>
        <option>Appartement</option>
        <option>Klein (&lt;50m²)</option>
      </select>
      <label>BTW:</label>
      <select id="filterBTW">
        <option value="">Alle regimes</option>
        <option>Nieuwbouw 21% BTW</option>
        <option>Nieuwbouw 6% BTW</option>
        <option>Bestaand (reg. rechten)</option>
      </select>
      <input type="text" id="searchBox" placeholder="🔍 Zoek adres, gemeente..." style="width:220px">
    </div>
  </div>

  <table id="listingsTable">
    <thead>
      <tr>
        <th onclick="sortTable(0)">Provincie</th>
        <th onclick="sortTable(1)">Adres</th>
        <th onclick="sortTable(2)">Postcode</th>
        <th onclick="sortTable(3)">Type</th>
        <th onclick="sortTable(4)" class="num">Opp. m²</th>
        <th onclick="sortTable(5)" class="num">Bouwjaar</th>
        <th onclick="sortTable(6)">BTW / Regime</th>
        <th onclick="sortTable(7)" class="num">Vraagprijs</th>
        <th onclick="sortTable(8)" class="num">€/m²</th>
        <th onclick="sortTable(9)">Bron</th>
      </tr>
    </thead>
    <tbody id="tableBody"></tbody>
  </table>

  <div class="pagination" id="pagination"></div>
  <div class="page-info" id="pageInfo" style="text-align:center;padding:8px;color:#666;font-size:.85rem"></div>
</div>

<footer>
  Wekelijks Vastgoedmarkt Rapport · Antwerpen · Vlaams-Brabant · Limburg
  · Data: Immoweb &amp; Zimmo (vraagprijzen, geen transactieprijzen) · {gegenereerd}
</footer>

<script>
const CHART_DATA   = {chart_json};
const ALL_LISTINGS = {all_data_json};

// ── Charts ──────────────────────────────────────────────────────────────────
const COLORS = {{
  woning:      ['#1B3A5C','#2E6DA4','#5B9BD5'],
  appartement: ['#217346','#70AD47','#A9D18E'],
  klein:       ['#C55A11','#ED7D31','#F4B183'],
  btw21:       ['#C55A11','#ED7D31','#F4B183'],
  btw6:        ['#217346','#70AD47','#A9D18E'],
  bestaand:    ['#5B2D8E','#8E5BB5','#C5A3E0'],
}};

new Chart(document.getElementById('chartProvType'), {{
  type: 'bar',
  data: {{
    labels: CHART_DATA.provincies,
    datasets: [
      {{ label: 'Woning',       data: CHART_DATA.per_prov_type['Woning'],
         backgroundColor: '#2E6DA4', borderRadius: 6 }},
      {{ label: 'Appartement',  data: CHART_DATA.per_prov_type['Appartement'],
         backgroundColor: '#70AD47', borderRadius: 6 }},
      {{ label: 'Klein (<50m²)',data: CHART_DATA.per_prov_type['Klein (<50m²)'],
         backgroundColor: '#ED7D31', borderRadius: 6 }},
    ]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ position: 'top' }},
               tooltip: {{ callbacks: {{ label: ctx => ` ${{ctx.dataset.label}}: ${{ctx.raw?.toLocaleString('nl-BE')}} €/m²` }} }} }},
    scales: {{
      y: {{ ticks: {{ callback: v => v.toLocaleString('nl-BE') + ' €' }}, grid: {{ color: '#EEE' }} }},
      x: {{ grid: {{ display: false }} }}
    }}
  }}
}});

new Chart(document.getElementById('chartBTW'), {{
  type: 'bar',
  data: {{
    labels: CHART_DATA.provincies,
    datasets: [
      {{ label: 'Nieuwbouw 21% BTW',      data: CHART_DATA.per_prov_btw['Nieuwbouw 21% BTW'],
         backgroundColor: '#C55A11', borderRadius: 6 }},
      {{ label: 'Nieuwbouw 6% BTW',       data: CHART_DATA.per_prov_btw['Nieuwbouw 6% BTW'],
         backgroundColor: '#70AD47', borderRadius: 6 }},
      {{ label: 'Bestaand (reg. rechten)',data: CHART_DATA.per_prov_btw['Bestaand (reg. rechten)'],
         backgroundColor: '#5B2D8E', borderRadius: 6 }},
    ]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ position: 'top' }},
               tooltip: {{ callbacks: {{ label: ctx => ` ${{ctx.dataset.label}}: ${{ctx.raw?.toLocaleString('nl-BE')}} €/m²` }} }} }},
    scales: {{
      y: {{ ticks: {{ callback: v => v.toLocaleString('nl-BE') + ' €' }}, grid: {{ color: '#EEE' }} }},
      x: {{ grid: {{ display: false }} }}
    }}
  }}
}});

// ── Tabel ────────────────────────────────────────────────────────────────────
let filtered = [...ALL_LISTINGS];
let sortCol = 8, sortDir = -1;
const PAGE_SIZE = 25;
let page = 1;

function btwClass(btw) {{
  if (btw.includes('21%')) return 'btw-21';
  if (btw.includes('6%'))  return 'btw-6';
  return 'btw-reg';
}}
function typeClass(t) {{
  if (t === 'Woning') return 'type-w';
  if (t === 'Appartement') return 'type-a';
  return 'type-k';
}}
function fmt(n) {{ return n ? n.toLocaleString('nl-BE') : '—'; }}

function renderTable() {{
  const tbody = document.getElementById('tableBody');
  const start = (page - 1) * PAGE_SIZE;
  const slice = filtered.slice(start, start + PAGE_SIZE);
  tbody.innerHTML = slice.map((r, i) => `
    <tr>
      <td>${{r.provincie}}</td>
      <td>${{r.adres}}</td>
      <td style="text-align:center">${{r.postcode}}</td>
      <td><span class="badge-type ${{typeClass(r.type)}}">${{r.type}}</span></td>
      <td class="num">${{r.oppervlakte_m2 ? r.oppervlakte_m2 + ' m²' : '—'}}</td>
      <td class="num">${{r.bouwjaar || '—'}}</td>
      <td><span class="badge-btw ${{btwClass(r.btw_regime)}}">${{r.btw_regime}}</span></td>
      <td class="num"><strong>${{r.prijs ? fmt(r.prijs) + ' €' : '—'}}</strong></td>
      <td class="num"><strong style="color:#1B3A5C">${{r.prijs_per_m2 ? fmt(r.prijs_per_m2) + ' €/m²' : '—'}}</strong></td>
      <td style="color:#555;font-size:.8rem">${{r.bron}}</td>
    </tr>
  `).join('');
  renderPagination();
}};

function renderPagination() {{
  const total = filtered.length;
  const totalPages = Math.ceil(total / PAGE_SIZE);
  const pag = document.getElementById('pagination');
  let html = '';
  if (totalPages <= 1) {{ pag.innerHTML = ''; return; }}
  html += `<button onclick="goPage(1)" ${{page===1?'disabled':''}}>«</button>`;
  html += `<button onclick="goPage(${{page-1}})" ${{page===1?'disabled':''}}>‹</button>`;
  const from = Math.max(1, page - 2), to = Math.min(totalPages, page + 2);
  for (let i = from; i <= to; i++)
    html += `<button onclick="goPage(${{i}})" class="${{i===page?'active':''}}">${{i}}</button>`;
  html += `<button onclick="goPage(${{page+1}})" ${{page===totalPages?'disabled':''}}>›</button>`;
  html += `<button onclick="goPage(${{totalPages}})" ${{page===totalPages?'disabled':''}}>»</button>`;
  pag.innerHTML = html;
  document.getElementById('pageInfo').textContent =
    `Toont ${{Math.min((page-1)*PAGE_SIZE+1, total)}}–${{Math.min(page*PAGE_SIZE, total)}} van ${{total}} listings`;
}}

function goPage(p) {{ page = p; renderTable(); window.scrollTo(0,600); }}

function applyFilters() {{
  const prov  = document.getElementById('filterProv').value;
  const type  = document.getElementById('filterType').value;
  const btw   = document.getElementById('filterBTW').value;
  const search = document.getElementById('searchBox').value.toLowerCase();
  filtered = ALL_LISTINGS.filter(r =>
    (!prov   || r.provincie === prov) &&
    (!type   || r.type === type) &&
    (!btw    || r.btw_regime === btw) &&
    (!search || (r.adres||'').toLowerCase().includes(search) ||
                (r.gemeente||'').toLowerCase().includes(search) ||
                (r.postcode||'').includes(search))
  );
  // Hertoepassen sortering
  doSort(sortCol, true);
  page = 1;
  renderTable();
}}

['filterProv','filterType','filterBTW','searchBox'].forEach(id =>
  document.getElementById(id).addEventListener('input', applyFilters));

let sortedCol = -1, sortedDir = 1;
const SORT_KEYS = ['provincie','adres','postcode','type','oppervlakte_m2','bouwjaar','btw_regime','prijs','prijs_per_m2','bron'];

function sortTable(col) {{
  if (sortedCol === col) sortedDir *= -1;
  else {{ sortedCol = col; sortedDir = 1; }}
  document.querySelectorAll('thead th').forEach((th, i) => {{
    th.classList.remove('sorted-asc','sorted-desc');
    if (i === col) th.classList.add(sortedDir === 1 ? 'sorted-asc' : 'sorted-desc');
  }});
  doSort(col, false);
  page = 1;
  renderTable();
}}

function doSort(col, keepDir) {{
  const key = SORT_KEYS[col];
  filtered.sort((a, b) => {{
    const va = a[key], vb = b[key];
    if (va == null) return 1; if (vb == null) return -1;
    return (va < vb ? -1 : va > vb ? 1 : 0) * (keepDir ? sortedDir : sortedDir);
  }});
}}

// Init: sorteer op prijs_per_m2 desc
sortedCol = 8; sortedDir = -1;
doSort(8, false);
document.querySelectorAll('thead th')[8].classList.add('sorted-desc');
renderTable();
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Dashboard opgeslagen: {output_path}")
    return output_path
