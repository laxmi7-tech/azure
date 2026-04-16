<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AzureScope — Sign In</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;900&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#04080f;--panel:#080e1a;--card:#0c1422;
  --border:#162035;--border2:#1e2f4a;
  --blue:#1d6fa4;--blue2:#2196d3;--blue3:#5ab4e0;
  --cyan:#00c8e8;--cyan2:#00e5ff;
  --text:#ddeeff;--muted:#5a7a9a;--muted2:#3a5570;
  --danger:#ff4d6d;--success:#00e5a0;
}
html,body{height:100%;overflow:hidden}
body{font-family:'Outfit',sans-serif;background:var(--bg);color:var(--text);display:flex;align-items:center;justify-content:center;position:relative}

/* Particle canvas bg */
canvas#bg{position:fixed;inset:0;z-index:0;opacity:.5}

/* Radial glow */
.glow-center{
  position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);
  width:700px;height:700px;background:radial-gradient(circle,rgba(0,200,232,.07) 0%,transparent 70%);
  pointer-events:none;z-index:1;
}

/* Main container */
.container{
  position:relative;z-index:10;width:100%;max-width:440px;padding:24px;
  animation:fadeUp .7s cubic-bezier(.22,1,.36,1) both;
}
@keyframes fadeUp{from{opacity:0;transform:translateY(32px)}to{opacity:1;transform:translateY(0)}}

/* Brand */
.brand{text-align:center;margin-bottom:40px}
.logo-ring{
  display:inline-flex;align-items:center;justify-content:center;
  width:64px;height:64px;border-radius:18px;margin-bottom:16px;
  background:linear-gradient(145deg,rgba(0,200,232,.15),rgba(29,111,164,.25));
  border:1px solid rgba(0,200,232,.25);
  box-shadow:0 0 40px rgba(0,200,232,.15),inset 0 1px 0 rgba(255,255,255,.05);
  font-size:28px;
}
.brand-name{
  font-family:'Outfit',sans-serif;font-weight:900;font-size:28px;
  letter-spacing:-1px;
  background:linear-gradient(135deg,#fff 30%,var(--cyan));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
.brand-tagline{font-size:13px;color:var(--muted);margin-top:4px;letter-spacing:.4px}

/* Card */
.card{
  background:rgba(8,14,26,.9);border:1px solid var(--border2);
  border-radius:20px;padding:36px 32px;
  backdrop-filter:blur(24px);
  box-shadow:0 32px 64px rgba(0,0,0,.5),0 0 0 1px rgba(0,200,232,.06),inset 0 1px 0 rgba(255,255,255,.04);
}
.card-title{font-size:20px;font-weight:700;margin-bottom:4px}
.card-sub{font-size:13px;color:var(--muted);margin-bottom:28px}

/* Credential hint */
.cred-hint{
  background:rgba(0,200,232,.06);border:1px solid rgba(0,200,232,.15);
  border-radius:10px;padding:12px 14px;margin-bottom:24px;
  display:flex;align-items:flex-start;gap:10px;
}
.cred-hint-icon{font-size:15px;margin-top:1px}
.cred-hint-text{font-size:12.5px;color:var(--blue3);line-height:1.6}
.cred-hint-text b{color:var(--cyan);font-family:'JetBrains Mono',monospace;font-weight:500}

/* Fields */
.field{margin-bottom:18px}
label{
  display:block;font-size:11px;font-weight:600;letter-spacing:.9px;
  text-transform:uppercase;color:var(--muted);margin-bottom:8px;
}
.input-wrap{position:relative}
input[type=text],input[type=password]{
  width:100%;background:rgba(255,255,255,.03);
  border:1px solid var(--border2);border-radius:10px;
  padding:13px 42px;color:var(--text);font-size:14px;
  font-family:'Outfit',sans-serif;outline:none;transition:all .25s;
}
input:focus{
  border-color:var(--cyan);background:rgba(0,200,232,.05);
  box-shadow:0 0 0 3px rgba(0,200,232,.1);
}
.fi{
  position:absolute;left:14px;top:50%;transform:translateY(-50%);
  width:16px;height:16px;opacity:.4;transition:opacity .2s;pointer-events:none;
}
input:focus ~ .fi, .input-wrap:focus-within .fi{opacity:1}
.toggle-pw{
  position:absolute;right:14px;top:50%;transform:translateY(-50%);
  background:none;border:none;cursor:pointer;color:var(--muted);
  display:flex;align-items:center;padding:4px;transition:color .2s;
}
.toggle-pw:hover{color:var(--cyan)}
.toggle-pw svg{width:16px;height:16px}

/* Error */
.error{
  display:none;align-items:center;gap:8px;
  background:rgba(255,77,109,.08);border:1px solid rgba(255,77,109,.25);
  border-radius:8px;padding:11px 14px;font-size:13px;color:#ff8099;
  margin-bottom:18px;
}
.error.show{display:flex}

/* Submit */
.btn{
  width:100%;padding:14px;margin-top:4px;
  background:linear-gradient(135deg,var(--blue2),var(--cyan));
  border:none;border-radius:10px;color:#fff;
  font-family:'Outfit',sans-serif;font-size:15px;font-weight:700;
  letter-spacing:.3px;cursor:pointer;position:relative;overflow:hidden;
  transition:all .25s;box-shadow:0 4px 20px rgba(0,200,232,.25);
}
.btn:hover{transform:translateY(-2px);box-shadow:0 8px 28px rgba(0,200,232,.35)}
.btn:active{transform:translateY(0)}
.btn.loading{pointer-events:none}
.btn .label{transition:opacity .2s}
.btn.loading .label{opacity:0}
.spin{
  display:none;position:absolute;top:50%;left:50%;
  transform:translate(-50%,-50%);
  width:18px;height:18px;border:2px solid rgba(255,255,255,.3);
  border-top-color:#fff;border-radius:50%;animation:spin .6s linear infinite;
}
@keyframes spin{to{transform:translate(-50%,-50%) rotate(360deg)}}
.btn.loading .spin{display:block}

/* Steps indicator */
.steps{display:flex;align-items:center;justify-content:center;gap:8px;margin-top:28px}
.step{
  display:flex;align-items:center;gap:6px;font-size:12px;
  padding:5px 12px;border-radius:20px;
}
.step.active{background:rgba(0,200,232,.12);border:1px solid rgba(0,200,232,.25);color:var(--cyan)}
.step.done{background:rgba(0,229,160,.08);border:1px solid rgba(0,229,160,.2);color:#00e5a0}
.step.inactive{border:1px solid var(--border2);color:var(--muted2)}
.step-dot{width:6px;height:6px;border-radius:50%;background:currentColor}
.step-sep{color:var(--muted2);font-size:10px}
</style>
</head>
<body>
<canvas id="bg"></canvas>
<div class="glow-center"></div>

<div class="container">
  <div class="brand">
    <div class="logo-ring">☁</div>
    <div class="brand-name">AzureScope</div>
    <div class="brand-tagline">Real-time Azure Cost Intelligence</div>
  </div>

  <div class="card">
    <div class="card-title">Sign in</div>
    <div class="card-sub">Access your Azure cost dashboard</div>

    <div class="cred-hint">
      <div class="cred-hint-icon">🔑</div>
      <div class="cred-hint-text">
        Username: <b>azureadmin</b><br>
        Password: <b>AzureScope@2024</b>
      </div>
    </div>

    <div class="error" id="errBox">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      <span id="errText">Invalid credentials</span>
    </div>

    <div class="field">
      <label>Username</label>
      <div class="input-wrap">
        <input type="text" id="username" placeholder="Enter username" autocomplete="username"/>
        <svg class="fi" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
      </div>
    </div>
    <div class="field">
      <label>Password</label>
      <div class="input-wrap">
        <input type="password" id="password" placeholder="Enter password" autocomplete="current-password"/>
        <svg class="fi" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        <button class="toggle-pw" onclick="togglePw()" type="button">
          <svg id="eyeSvg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
        </button>
      </div>
    </div>

    <button class="btn" id="loginBtn" onclick="doLogin()">
      <span class="label">Sign In →</span>
      <div class="spin"></div>
    </button>
  </div>

  <div class="steps">
    <div class="step active"><div class="step-dot"></div>Sign In</div>
    <div class="step-sep">›</div>
    <div class="step inactive"><div class="step-dot"></div>Azure Connect</div>
    <div class="step-sep">›</div>
    <div class="step inactive"><div class="step-dot"></div>Cost Dashboard</div>
  </div>
</div>

<script>
// Particle background
(function(){
  const c=document.getElementById('bg'),ctx=c.getContext('2d');
  let W,H,pts=[];
  function resize(){W=c.width=innerWidth;H=c.height=innerHeight;pts=[];for(let i=0;i<60;i++)pts.push({x:Math.random()*W,y:Math.random()*H,vx:(Math.random()-.5)*.3,vy:(Math.random()-.5)*.3,r:Math.random()*1.5+.5})}
  resize();window.addEventListener('resize',resize);
  function draw(){
    ctx.clearRect(0,0,W,H);
    pts.forEach(p=>{p.x+=p.vx;p.y+=p.vy;if(p.x<0||p.x>W)p.vx*=-1;if(p.y<0||p.y>H)p.vy*=-1;ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fillStyle='rgba(0,200,232,.4)';ctx.fill()});
    pts.forEach((a,i)=>pts.slice(i+1).forEach(b=>{const d=Math.hypot(a.x-b.x,a.y-b.y);if(d<100){ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.strokeStyle=`rgba(0,200,232,${.12*(1-d/100)})`;ctx.stroke()}}));
    requestAnimationFrame(draw);
  }
  draw();
})();

function togglePw(){
  const p=document.getElementById('password');
  p.type=p.type==='password'?'text':'password';
}

async function doLogin(){
  const u=document.getElementById('username').value.trim();
  const p=document.getElementById('password').value.trim();
  const btn=document.getElementById('loginBtn');
  const err=document.getElementById('errBox');
  err.classList.remove('show');
  if(!u||!p){showErr('Please enter username and password.');return;}
  btn.classList.add('loading');
  try{
    const r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});
    const d=await r.json();
    if(r.ok){window.location.href='/connect';}
    else{showErr(d.detail||'Invalid credentials.');}
  }catch(e){showErr('Connection error. Please retry.');}
  btn.classList.remove('loading');
}
function showErr(msg){
  document.getElementById('errText').textContent=msg;
  document.getElementById('errBox').classList.add('show');
}
document.addEventListener('keydown',e=>{if(e.key==='Enter')doLogin();});
</script>
</body>
</html>
