# ruff: noqa: E501
"""Generate the public dashboard (docs/index.html) from the Ninca database."""

from __future__ import annotations

import json
from pathlib import Path

from ninca.storage import connect

OUTPUT = Path("docs/index.html")

_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>State of MCP Server Security</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.4/chart.umd.min.js"></script>
<style>
  :root { color-scheme: dark; }
  body { margin:0; font-family: system-ui, sans-serif; background:#0d1117; color:#e6edf3; }
  header { padding:40px 20px; text-align:center; border-bottom:1px solid #30363d; }
  header h1 { margin:0; font-size:2rem; }
  header p { color:#8b949e; }
  .wrap { max-width:900px; margin:0 auto; padding:20px; }
  .cards { display:flex; gap:16px; flex-wrap:wrap; margin:24px 0; }
  .card { flex:1; min-width:150px; background:#161b22; border:1px solid #30363d; border-radius:10px; padding:20px; text-align:center; }
  .card .num { font-size:2rem; font-weight:700; color:#58a6ff; }
  .card .label { color:#8b949e; font-size:.9rem; }
  .box { background:#161b22; border:1px solid #30363d; border-radius:10px; padding:20px; margin:16px 0; }
  h2 { font-size:1.2rem; }
  footer { text-align:center; color:#8b949e; padding:30px; font-size:.85rem; }
  a { color:#58a6ff; }
</style>
</head>
<body>
<header>
  <h1>State of MCP Server Security</h1>
  <p>An open-source scan of the Model Context Protocol ecosystem, built with Ninca</p>
</header>
<div class="wrap">
  <div class="cards">
    <div class="card"><div class="num" id="total">0</div><div class="label">servers discovered</div></div>
    <div class="card"><div class="num" id="enriched">0</div><div class="label">analyzed (sample)</div></div>
    <div class="card"><div class="num">6+</div><div class="label">detection rules</div></div>
    <div class="card"><div class="num">AI</div><div class="label">hybrid classifier</div></div>
  </div>
  <div class="box"><h2>Top languages (sample)</h2><canvas id="langChart"></canvas></div>
  <div class="box"><h2>Licenses (sample)</h2><canvas id="licChart"></canvas></div>
  <div class="box">
    <h2>Detection recall (higher is better)</h2>
    <canvas id="recallChart"></canvas>
    <p style="color:#8b949e">Adding an AI classifier raised recall from 57% to 86% with zero false positives.</p>
  </div>
</div>
<footer>Built in Manta, Ecuador &middot; <a href="https://github.com/Fabricioanchundia/NINCA">github.com/Fabricioanchundia/NINCA</a></footer>
<script>
const DATA = __DATA__;
document.getElementById('total').textContent = DATA.total_servers.toLocaleString();
document.getElementById('enriched').textContent = DATA.enriched_servers.toLocaleString();
const blue = '#58a6ff';
function bar(id, pairs) {
  new Chart(document.getElementById(id), {
    type: 'bar',
    data: { labels: pairs.map(p => p[0]), datasets: [{ data: pairs.map(p => p[1]), backgroundColor: blue }] },
    options: { plugins: { legend: { display:false } }, scales: { x:{ticks:{color:'#8b949e'}}, y:{ticks:{color:'#8b949e'}} } }
  });
}
bar('langChart', DATA.languages);
bar('licChart', DATA.licenses);
new Chart(document.getElementById('recallChart'), {
  type:'bar',
  data:{ labels:['Rules only','AI only','Hybrid'], datasets:[{ data:[0.57,0.86,0.86], backgroundColor:blue }] },
  options:{ plugins:{legend:{display:false}}, scales:{ y:{min:0,max:1,ticks:{color:'#8b949e'}}, x:{ticks:{color:'#8b949e'}} } }
});
</script>
</body>
</html>
"""


def main() -> None:
    connection = connect()
    total = connection.execute("SELECT count(*) FROM servers").fetchone()
    enriched = connection.execute("SELECT count(*) FROM servers WHERE stars IS NOT NULL").fetchone()
    languages = connection.execute(
        "SELECT coalesce(nullif(language, ''), 'unknown') AS lang, count(*) "
        "FROM servers WHERE stars IS NOT NULL GROUP BY lang ORDER BY count(*) DESC LIMIT 8"
    ).fetchall()
    licenses = connection.execute(
        "SELECT coalesce(nullif(license, ''), 'none') AS lic, count(*) "
        "FROM servers WHERE stars IS NOT NULL GROUP BY lic ORDER BY count(*) DESC LIMIT 8"
    ).fetchall()
    connection.close()
    data = {
        "total_servers": int(total[0]) if total else 0,
        "enriched_servers": int(enriched[0]) if enriched else 0,
        "languages": [[str(r[0]), int(r[1])] for r in languages],
        "licenses": [[str(r[0]), int(r[1])] for r in licenses],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(_TEMPLATE.replace("__DATA__", json.dumps(data)), encoding="utf-8")
    print(f"Wrote {OUTPUT}: {data['total_servers']} servers, {data['enriched_servers']} enriched.")


if __name__ == "__main__":
    main()
