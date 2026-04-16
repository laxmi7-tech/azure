<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AzureScope — Cost Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;900&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#04080f;--panel:#080e1a;--card:#0c1422;--card2:#0e1828;
  --border:#162035;--border2:#1e2f4a;
  --blue:#1d6fa4;--blue2:#2196d3;--blue3:#5ab4e0;
  --cyan:#00c8e8;--cyan2:#00e5ff;
  --text:#ddeeff;--muted:#5a7a9a;--muted2:#3a5570;
  --danger:#ff4d6d;--success:#00e5a0;--warn:#f59e0b;
  --amort:#a78bfa;--actual:#38bdf8;
}
html{scroll-behavior:smooth}
body{font-family:'Outfit',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;display:flex;flex-direction:column}

/* Nav */
.nav{
  display:flex;align-items:center;justify-content:space-between;
  padding:14px 28px;border-bottom:1px solid var(--border);
  background:rgba(8,14,26,.9);backdrop-filter:blur(12px);
  position:sticky;top:0;z-index:100;
}
.nav-brand{display:flex;align-items:center;gap:10px;text-decoration:none}
.nav-logo{width:34px;height:34px;background:linear-gradient(145deg,rgba(0,200,232,.2),rgba(29,111,164,.3));border:1px solid rgba(0,200,232,.2);border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:17px}
.nav-name{font-weight:900;font-size:16px;background:linear-gradient(135deg,#fff,var(--cyan));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.nav-right{display:flex;align-items:center;gap:10px}
.nav-pill{font-size:12px;padding:5px 12px;border:1px solid var(--border2);border-radius:20px;color:var(--muted)}
.nav-pill.green{border-color:rgba(0,229,160,.25);color:#00e5a0;background:rgba(0,229,160,.06)}
.nav-link{font-size:13px;color:var(--muted);padding:6px 12px;border:1px solid var(--border2);border-radius:7px;text-decoration:none;transition:all .2s}
.nav-link:hover{color:var(--text);border-color:var(--border)}
.nav-logout{font-size:13px;color:var(--muted);padding:6px 12px;background:none;border:1px solid var(--border2);border-radius:7px;cursor:pointer;transition:all .2s;text-decoration:none}
.nav-logout:hover{color:var(--danger);border-color:rgba(255,77,109,.3)}

/* Steps */
.steps-bar{display:flex;align-items:center;justify-content:center;gap:0;padding:24px 0 0}
.stp{display:flex;align-items:center;gap:10px;font-size:13px;padding:7px 16px;border-radius:24px;cursor:default;text-decoration:none}
.stp.done{background:rgba(0,229,160,.08);border:1px solid rgba(0,229,160,.2);color:#00e5a0}
.stp.done:hover{background:rgba(0,229,160,.14)}
.stp.active{background:rgba(0,200,232,.12);border:1px solid rgba(0,200,232,.3);color:var(--cyan)}
.stp-num{width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;background:currentColor;color:var(--bg)}
.stp-sep{color:var(--muted2);margin:0 4px;font-size:14px}

/* Main layout */
.main{flex:1;padding:28px 24px 60px;max-width:1200px;width:100%;margin:0 auto}

/* Header row */
.dash-header{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:28px;flex-wrap:wrap;gap:14px;animation:fadeUp .4s ease both}
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
.dash-title h1{font-size:22px;font-weight:800;margin-bottom:4px}
.dash-title p{font-size:13px;color:var(--muted)}
.dash-controls{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.date-label{font-size:12px;color:var(--muted);font-weight:500}
.date-input{
  background:rgba(255,255,255,.04);border:1px solid var(--border2);border-radius:8px;
  padding:8px 12px;color:var(--text);font-size:13px;font-family:'Outfit',sans-serif;outline:none;
  color-scheme:dark;
}
.date-input:focus{border-color:var(--cyan)}
.btn-fetch{
  padding:9px 18px;background:linear-gradient(135deg,var(--blue2),var(--cyan));
  border:none;border-radius:8px;color:#fff;font-family:'Outfit',sans-serif;
  font-size:13px;font-weight:700;cursor:pointer;transition:all .2s;
  box-shadow:0 3px 14px rgba(0,200,232,.2);display:flex;align-items:center;gap:6px;
}
.btn-fetch:hover{transform:translateY(-1px);box-shadow:0 5px 18px rgba(0,200,232,.3)}
.btn-fetch.loading{opacity:.7;pointer-events:none}

/* Tab switcher */
.tab-bar{display:flex;gap:6px;background:rgba(255,255,255,.03);border:1px solid var(--border2);border-radius:12px;padding:5px;margin-bottom:24px;width:fit-content;animation:fadeUp .4s .05s ease both}
.tab{
  padding:9px 20px;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;
  transition:all .2s;color:var(--muted);display:flex;align-items:center;gap:7px;
}
.tab:hover{color:var(--text)}
.tab.active-actual{background:rgba(56,189,248,.15);border:1px solid rgba(56,189,248,.3);color:var(--actual)}
.tab.active-amort{background:rgba(167,139,250,.15);border:1px solid rgba(167,139,250,.3);color:var(--amort)}
.tab-dot{width:8px;height:8px;border-radius:50%;background:currentColor}

/* Summary cards */
.summary-row{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:24px;animation:fadeUp .4s .1s ease both}
.sum-card{
  background:var(--card);border:1px solid var(--border2);border-radius:14px;
  padding:20px;position:relative;overflow:hidden;transition:transform .2s;
}
.sum-card:hover{transform:translateY(-2px)}
.sum-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--accent,var(--cyan))}
.sc-label{font-size:11px;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);margin-bottom:10px}
.sc-value{font-family:'JetBrains Mono',monospace;font-size:28px;font-weight:700;margin-bottom:6px}
.sc-change{font-size:12px;display:flex;align-items:center;gap:4px}
.sc-change.up{color:#ff8099}.sc-change.down{color:#00e5a0}.sc-change.neutral{color:var(--muted)}
.sc-icon{position:absolute;top:16px;right:16px;font-size:26px;opacity:.12}
.skeleton{animation:shimmer 1.4s infinite;background:linear-gradient(90deg,var(--card) 25%,var(--card2) 50%,var(--card) 75%);background-size:200% 100%}
@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}

/* Cost type badges */
.type-badge{
  display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:20px;
  font-size:12px;font-weight:600;
}
.badge-actual{background:rgba(56,189,248,.12);border:1px solid rgba(56,189,248,.25);color:var(--actual)}
.badge-amort{background:rgba(167,139,250,.12);border:1px solid rgba(167,139,250,.25);color:var(--amort)}

/* Charts row */
.charts-row{display:grid;grid-template-columns:3fr 2fr;gap:16px;margin-bottom:24px;animation:fadeUp .4s .15s ease both}
.chart-card{background:var(--card);border:1px solid var(--border2);border-radius:14px;padding:22px}
.chart-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
.chart-title{font-size:14px;font-weight:700}
.chart-sub{font-size:12px;color:var(--muted)}

/* Services table */
.table-card{background:var(--card);border:1px solid var(--border2);border-radius:14px;overflow:hidden;animation:fadeUp .4s .2s ease both}
.table-head-row{padding:18px 20px 14px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between}
.table-title{font-size:14px;font-weight:700}
table{width:100%;border-collapse:collapse}
thead th{padding:11px 18px;text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.7px;color:var(--muted);background:rgba(255,255,255,.02);font-weight:600}
tbody tr{border-bottom:1px solid var(--border);transition:background .15s;cursor:default}
tbody tr:hover{background:rgba(0,200,232,.04)}
tbody tr:last-child{border:none}
td{padding:13px 18px;font-size:13.5px}
.svc-name{font-weight:500}
.cost-val{font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:600}
.bar-wrap{display:flex;align-items:center;gap:8px}
.bar{background:rgba(255,255,255,.06);border-radius:4px;height:6px;flex:1;max-width:120px;overflow:hidden}
.bar-fill{height:100%;border-radius:4px;background:linear-gradient(90deg,var(--blue2),var(--cyan))}
.pct-txt{font-size:12px;color:var(--muted);min-width:36px}

/* Empty state */
.empty{padding:60px;text-align:center;color:var(--muted)}
.empty-icon{font-size:40px;margin-bottom:12px}
.empty-title{font-size:16px;font-weight:600;margin-bottom:6px;color:var(--text)}
.empty-sub{font-size:13px;line-height:1.6}

/* Error/Loading */
.loading-state{padding:50px;text-align:center;color:var(--muted)}
.loader{display:inline-block;width:28px;height:28px;border:2px solid rgba(0,200,232,.2);border-top-color:var(--cyan);border-radius:50%;animation:spin .7s linear infinite;margin-bottom:14px}
@keyframes spin{to{transform:rotate(360deg)}}
.err-state{padding:40px;text-align:center}
.err-box{background:rgba(255,77,109,.07);border:1px solid rgba(255,77,109,.2);border-radius:10px;padding:16px;display:inline-block;max-width:460px;font-size:13px;color:#ff8099;line-height:1.6}

@media(max-width:900px){
  .charts-row{grid-template-columns:1fr}
  .summary-row{grid-template-columns:1fr 1fr}
}
@media(max-width:600px){
  .summary-row{grid-template-columns:1fr}
  .main{padding:16px 14px 40px}
}
</style>
</head>
<body>
<nav class="nav">
  <a class="nav-brand" href="/connect">
    <div class="nav-logo">☁</div>
    <div class="nav-name">AzureScope</div>
  </a>
  <div class="nav-right">
    <div class="nav-pill green" id="subPill">Loading…</div>
    <div class="nav-pill" id="navUser">…</div>
    <a href="/connect" class="nav-link">⚙ Reconnect</a>
    <a href="/logout" class="nav-logout">Logout</a>
  </div>
</nav>

<div>
  <div class="steps-bar">
    <a href="/" class="stp done"><div class="stp-num">✓</div>Sign In</a>
    <span class="stp-sep">›</span>
    <a href="/connect" class="stp done"><div class="stp-num">✓</div>Azure Connect</a>
    <span class="stp-sep">›</span>
    <div class="stp active"><div class="stp-num">3</div>Cost Dashboard</div>
  </div>
</div>

<main class="main">
  <!-- Header -->
  <div class="dash-header">
    <div class="dash-title">
      <h1>💰 Azure Cost Dashboard</h1>
      <p id="periodLabel">Loading cost data…</p>
    </div>
    <div class="dash-controls">
      <span class="date-label">From</span>
      <input type="date" id="startDate" class="date-input"/>
      <span class="date-label">To</span>
      <input type="date" id="endDate" class="date-input"/>
      <button class="btn-fetch" id="fetchBtn" onclick="fetchAll()">
        <span>↻</span><span>Refresh</span>
      </button>
    </div>
  </div>

  <!-- Tab bar -->
  <div class="tab-bar">
    <div class="tab active-actual" id="tabActual" onclick="switchTab('actual')">
      <div class="tab-dot"></div> Actual Cost
    </div>
    <div class="tab" id="tabAmort" onclick="switchTab('amortized')">
      <div class="tab-dot" style="background:var(--amort)"></div> Amortized Cost
    </div>
    <div class="tab" id="tabBoth" onclick="switchTab('both')">
      <div class="tab-dot" style="background:#facc15"></div> Compare Both
    </div>
  </div>

  <!-- Summary Cards -->
  <div class="summary-row" id="summaryRow">
    <div class="sum-card skeleton" style="height:110px"></div>
    <div class="sum-card skeleton" style="height:110px"></div>
    <div class="sum-card skeleton" style="height:110px"></div>
  </div>

  <!-- Charts -->
  <div class="charts-row" id="chartsRow">
    <div class="chart-card">
      <div class="chart-header">
        <div><div class="chart-title">Daily Cost Trend</div><div class="chart-sub" id="trendSub">Loading…</div></div>
        <div id="trendBadge"></div>
      </div>
      <canvas id="trendChart" height="90"></canvas>
    </div>
    <div class="chart-card">
      <div class="chart-header">
        <div><div class="chart-title">Top Services</div><div class="chart-sub">Cost share by service</div></div>
      </div>
      <canvas id="donutChart" height="160"></canvas>
    </div>
  </div>

  <!-- Services table -->
  <div class="table-card" id="tableCard">
    <div class="table-head-row">
      <div class="table-title" id="tableTitle">Service Cost Breakdown</div>
      <div id="tableBadge"></div>
    </div>
    <div id="tableBody">
      <div class="loading-state">
        <div class="loader"></div>
        <div>Fetching data from Azure Cost Management…</div>
      </div>
    </div>
  </div>
</main>

<script>
let trendChart=null, donutChart=null;
let dataActual=null, dataAmort=null, dataSummary=null;
let currentTab='actual';

// Init dates
const now=new Date();
const firstDay=new Date(now.getFullYear(),now.getMonth(),1).toISOString().split('T')[0];
const today=now.toISOString().split('T')[0];
document.getElementById('startDate').value=firstDay;
document.getElementById('endDate').value=today;

// Load session
fetch('/api/session/status').then(r=>r.json()).then(d=>{
  if(!d.authenticated){window.location.href='/';return;}
  if(!d.azure_connected){window.location.href='/connect';return;}
  document.getElementById('navUser').textContent='👤 '+d.username;
  document.getElementById('subPill').textContent='🔗 '+d.subscription_id.slice(0,8)+'…';
  fetchAll();
});

async function fetchAll(){
  const start=document.getElementById('startDate').value;
  const end=document.getElementById('endDate').value;
  const btn=document.getElementById('fetchBtn');
  btn.classList.add('loading');
  document.getElementById('periodLabel').textContent=`Period: ${start} → ${end}`;
  document.getElementById('tableBody').innerHTML=`<div class="loading-state"><div class="loader"></div><div>Fetching from Azure…</div></div>`;

  try{
    const [actualRes, amortRes, summaryRes] = await Promise.all([
      fetch(`/api/costs/actual?start_date=${start}&end_date=${end}`),
      fetch(`/api/costs/amortized?start_date=${start}&end_date=${end}`),
      fetch('/api/costs/summary')
    ]);

    if(!actualRes.ok){const e=await actualRes.json();throw new Error(e.detail||'Failed to fetch actual costs');}
    if(!amortRes.ok){const e=await amortRes.json();throw new Error(e.detail||'Failed to fetch amortized costs');}

    dataActual=await actualRes.json();
    dataAmort=await amortRes.json();
    dataSummary=summaryRes.ok ? await summaryRes.json() : null;

    renderSummary();
    renderTab(currentTab);
  }catch(e){
    document.getElementById('tableBody').innerHTML=`<div class="err-state"><div class="err-box">⚠ ${e.message}</div></div>`;
    document.getElementById('summaryRow').innerHTML='<div style="grid-column:1/-1;color:var(--muted);font-size:13px;padding:10px 0">Could not load cost summary.</div>';
  }
  btn.classList.remove('loading');
}

function fmt(v){return'$'+Number(v).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2})}
function fmtShort(v){
  if(v>=1000000)return'$'+(v/1000000).toFixed(2)+'M';
  if(v>=1000)return'$'+(v/1000).toFixed(1)+'K';
  return'$'+v.toFixed(2);
}

function renderSummary(){
  const s=dataSummary;
  const a=dataActual;
  const am=dataAmort;
  if(!a){return;}

  const changePct=(curr,prev)=>{
    if(!prev||prev===0)return{pct:0,dir:'neutral'};
    const p=((curr-prev)/prev*100).toFixed(1);
    return{pct:Math.abs(p),dir:p>0?'up':'down'};
  };

  const actualChg=s?changePct(s.actual.current_month,s.actual.last_month):{pct:0,dir:'neutral'};
  const amortChg=s?changePct(s.amortized.current_month,s.amortized.last_month):{pct:0,dir:'neutral'};

  document.getElementById('summaryRow').innerHTML=`
    <div class="sum-card" style="--accent:var(--actual)">
      <div class="sc-label">Actual Cost (MTD)</div>
      <div class="sc-value" style="color:var(--actual)">${fmt(a.total)}</div>
      <div class="sc-change ${actualChg.dir}">${actualChg.dir==='up'?'↑':'↓'} ${actualChg.pct}% vs last month</div>
      <div class="sc-icon">💳</div>
    </div>
    <div class="sum-card" style="--accent:var(--amort)">
      <div class="sc-label">Amortized Cost (MTD)</div>
      <div class="sc-value" style="color:var(--amort)">${fmt(am.total)}</div>
      <div class="sc-change ${amortChg.dir}">${amortChg.dir==='up'?'↑':'↓'} ${amortChg.pct}% vs last month</div>
      <div class="sc-icon">📦</div>
    </div>
    <div class="sum-card" style="--accent:var(--success)">
      <div class="sc-label">Services Tracked</div>
      <div class="sc-value" style="color:var(--success)">${a.service_count}</div>
      <div class="sc-change neutral">Across your subscription</div>
      <div class="sc-icon">☁</div>
    </div>`;
}

function switchTab(tab){
  currentTab=tab;
  ['actual','amortized','both'].forEach(t=>{
    const el=document.getElementById('tab'+t.charAt(0).toUpperCase()+t.slice(1).replace('ized',''));
    if(!el)return;
    el.className='tab';
  });
  document.getElementById('tabActual').className='tab'+(tab==='actual'?' active-actual':tab==='both'?' active-actual':'');
  document.getElementById('tabAmort').className='tab'+(tab==='amortized'?' active-amort':tab==='both'?' active-amort':'');
  document.getElementById('tabBoth').className='tab'+(tab==='both'?' active-actual':'');
  if(dataActual)renderTab(tab);
}

function renderTab(tab){
  if(tab==='actual')renderSingle(dataActual,'actual');
  else if(tab==='amortized')renderSingle(dataAmort,'amortized');
  else renderBoth();
}

function renderSingle(data, type){
  const color=type==='actual'?'rgba(56,189,248,.8)':'rgba(167,139,250,.8)';
  const fill=type==='actual'?'rgba(56,189,248,.1)':'rgba(167,139,250,.1)';
  const label=type==='actual'?'Actual Cost':'Amortized Cost';

  // Trend chart
  renderTrendChart(
    data.daily_trend.map(d=>d.date),
    [{label,data:data.daily_trend.map(d=>d.cost),borderColor:color,backgroundColor:fill}]
  );
  document.getElementById('trendSub').textContent=`${data.period.start} → ${data.period.end}`;
  document.getElementById('trendBadge').innerHTML=`<span class="type-badge badge-${type==='actual'?'actual':'amort'}">${label}</span>`;

  // Donut
  renderDonut(data.top_services.slice(0,6));

  // Table
  renderTable(data, type);
  document.getElementById('tableTitle').textContent=`${label} — Top Services`;
  document.getElementById('tableBadge').innerHTML=`<span class="type-badge badge-${type==='actual'?'actual':'amort'}">${fmt(data.total)} total</span>`;
}

function renderBoth(){
  if(!dataActual||!dataAmort)return;
  // Merge dates
  const allDates=[...new Set([...dataActual.daily_trend.map(d=>d.date),...dataAmort.daily_trend.map(d=>d.date)])].sort();
  const aMap=Object.fromEntries(dataActual.daily_trend.map(d=>[d.date,d.cost]));
  const mMap=Object.fromEntries(dataAmort.daily_trend.map(d=>[d.date,d.cost]));

  renderTrendChart(allDates,[
    {label:'Actual Cost',data:allDates.map(d=>aMap[d]||0),borderColor:'rgba(56,189,248,.9)',backgroundColor:'rgba(56,189,248,.08)'},
    {label:'Amortized Cost',data:allDates.map(d=>mMap[d]||0),borderColor:'rgba(167,139,250,.9)',backgroundColor:'rgba(167,139,250,.08)'}
  ]);
  document.getElementById('trendSub').textContent='Actual vs Amortized comparison';
  document.getElementById('trendBadge').innerHTML='<span class="type-badge" style="background:rgba(250,204,21,.1);border-color:rgba(250,204,21,.3);color:#facc15">Comparison</span>';

  // Donut uses actual
  renderDonut(dataActual.top_services.slice(0,6));

  // Table: side by side
  renderCompareTable();
  document.getElementById('tableTitle').textContent='Side-by-Side Cost Comparison';
  document.getElementById('tableBadge').innerHTML='<span class="type-badge badge-actual">Actual</span> vs <span class="type-badge badge-amort" style="margin-left:4px">Amortized</span>';
}

function renderTrendChart(labels, datasets){
  if(trendChart)trendChart.destroy();
  const ctx=document.getElementById('trendChart').getContext('2d');
  trendChart=new Chart(ctx,{
    type:'line',
    data:{labels,datasets:datasets.map(ds=>({...ds,borderWidth:2,pointRadius:0,tension:.4}))},
    options:{
      responsive:true,animation:{duration:600},
      plugins:{legend:{display:datasets.length>1,position:'top',labels:{color:'#5a7a9a',boxWidth:10,font:{size:11}}}},
      scales:{
        x:{ticks:{color:'#3a5570',maxTicksLimit:10,font:{size:10}},grid:{color:'rgba(255,255,255,.04)'}},
        y:{ticks:{color:'#3a5570',callback:v=>fmtShort(v),font:{size:10}},grid:{color:'rgba(255,255,255,.04)'}}
      }
    }
  });
}

const COLORS=['#38bdf8','#818cf8','#34d399','#fb923c','#f472b6','#facc15','#60a5fa'];
function renderDonut(services){
  if(donutChart)donutChart.destroy();
  const ctx=document.getElementById('donutChart').getContext('2d');
  donutChart=new Chart(ctx,{
    type:'doughnut',
    data:{
      labels:services.map(s=>s.service.length>20?s.service.slice(0,20)+'…':s.service),
      datasets:[{data:services.map(s=>s.cost),backgroundColor:COLORS,borderWidth:2,borderColor:'#0c1422'}]
    },
    options:{
      cutout:'65%',animation:{duration:600},
      plugins:{
        legend:{position:'right',labels:{color:'#5a7a9a',boxWidth:10,font:{size:11},padding:8}},
        tooltip:{callbacks:{label:c=>` ${fmt(c.raw)}`}}
      }
    }
  });
}

function renderTable(data, type){
  const color=type==='actual'?'var(--actual)':'var(--amort)';
  if(!data.top_services.length){
    document.getElementById('tableBody').innerHTML='<div class="empty"><div class="empty-icon">📭</div><div class="empty-title">No cost data found</div><div class="empty-sub">No charges found for the selected period. Try a broader date range.</div></div>';
    return;
  }
  const max=data.top_services[0].cost;
  document.getElementById('tableBody').innerHTML=`
    <table>
      <thead><tr>
        <th>#</th><th>Service Name</th>
        <th>Cost</th><th>% of Total</th><th>Distribution</th>
      </tr></thead>
      <tbody>
        ${data.top_services.map((s,i)=>`
          <tr>
            <td style="color:var(--muted);font-size:12px">${i+1}</td>
            <td><div class="svc-name">${s.service}</div></td>
            <td><div class="cost-val" style="color:${color}">${fmt(s.cost)}</div></td>
            <td style="color:var(--muted);font-size:13px">${s.pct}%</td>
            <td>
              <div class="bar-wrap">
                <div class="bar"><div class="bar-fill" style="width:${(s.cost/max*100).toFixed(1)}%;background:linear-gradient(90deg,${color},${color}aa)"></div></div>
                <span class="pct-txt">${s.pct}%</span>
              </div>
            </td>
          </tr>`).join('')}
      </tbody>
    </table>`;
}

function renderCompareTable(){
  const svcMap={};
  dataActual.top_services.forEach(s=>{svcMap[s.service]={...svcMap[s.service],actual:s.cost,pct_actual:s.pct}});
  dataAmort.top_services.forEach(s=>{svcMap[s.service]={...svcMap[s.service],amort:s.cost,pct_amort:s.pct}});
  const rows=Object.entries(svcMap).sort((a,b)=>(b[1].actual||0)-(a[1].actual||0)).slice(0,15);
  document.getElementById('tableBody').innerHTML=`
    <table>
      <thead><tr>
        <th>Service</th>
        <th style="color:var(--actual)">Actual Cost</th>
        <th style="color:var(--amort)">Amortized Cost</th>
        <th>Difference</th>
      </tr></thead>
      <tbody>
        ${rows.map(([svc,vals])=>{
          const diff=(vals.amort||0)-(vals.actual||0);
          const diffColor=diff>0?'var(--amort)':diff<0?'var(--actual)':'var(--muted)';
          return`<tr>
            <td><div class="svc-name">${svc}</div></td>
            <td><div class="cost-val" style="color:var(--actual)">${fmt(vals.actual||0)}</div></td>
            <td><div class="cost-val" style="color:var(--amort)">${fmt(vals.amort||0)}</div></td>
            <td style="color:${diffColor};font-family:'JetBrains Mono',monospace;font-size:13px">${diff>=0?'+':''}${fmt(diff)}</td>
          </tr>`;}).join('')}
      </tbody>
    </table>`;
}
</script>
</body>
</html>
