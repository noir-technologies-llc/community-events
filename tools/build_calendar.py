"""Build the self-contained, filterable Community Events calendar (HTML) from data/events.json.
Shows a rolling window: the Monday of the as-of week through the end of the same month one year later.
Usage: python3 build_calendar.py "Month D, YYYY" > Community-Events-Calendar.html
"""
import json, sys, html, calendar as _cal
from datetime import date as _date, datetime as _dt, timedelta as _td
data = json.load(open('data/events.json'))
as_of = sys.argv[1] if len(sys.argv) > 1 else data.get('updated', '')
try: _t = _dt.strptime(as_of, '%B %d, %Y').date()
except ValueError: _t = _date.fromisoformat(as_of)
W0 = _t - _td(days=_t.weekday())
_ey, _em = _t.year + 1, _t.month
W1 = _date(_ey, _em, _cal.monthrange(_ey, _em)[1])
MONTHS = []
_y, _m = W0.year, W0.month
while (_y, _m) <= (W1.year, W1.month):
    MONTHS.append([_date(_y,_m,1).isoformat(), _date(_y,_m,_cal.monthrange(_y,_m)[1]).isoformat(), _date(_y,_m,1).strftime('%B %Y')])
    _y, _m = (_y + (_m == 12), 1 if _m == 12 else _m + 1)
SCOPE = f"{W0.strftime('%B')} {W0.day}, {W0.year} to {W1.strftime('%B')} {W1.day}, {W1.year}"
payload = json.dumps(data['events']).replace('</', '<\\/')

TEMPLATE = r'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Community Events · Richmond and Hampton Roads</title>
<style>
:root{--paper:#F6F5F0;--ink:#212322;--red:#A72B2A;--gold:#9B9576;--slate:#707372;--line:#E2DFD3;--soft:#EFEDE4}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:Arial,Helvetica,sans-serif;line-height:1.5}
a{color:var(--red)}
.wrap{max-width:900px;margin:0 auto;padding:0 18px}
header{background:var(--ink);color:var(--paper);padding:28px 0 22px;border-bottom:4px solid var(--red)}
.kicker{font-size:11px;letter-spacing:2px;text-transform:uppercase;color:var(--gold);font-weight:bold}
h1{font-family:Georgia,serif;font-size:46px;margin:6px 0 2px;line-height:1}
h1 i{font-weight:normal}
.dek{color:#D8D5C6;font-size:14px;margin:0}
.asof{color:#BDB9A8;font-size:12px;margin-top:10px}
.panel{position:sticky;top:0;z-index:5;background:var(--paper);border-bottom:1px solid var(--line);padding:12px 0}
.row{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:6px 0}
.lbl{font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:var(--slate);font-weight:bold;min-width:96px}
.chip{border:1px solid var(--line);background:#fff;color:var(--ink);font:600 13px Arial,sans-serif;padding:7px 12px;border-radius:999px;cursor:pointer}
.chip[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
select,input[type=search]{font:14px Arial,sans-serif;padding:7px 10px;border:1px solid var(--line);border-radius:6px;background:#fff;color:var(--ink)}
#orgsel{min-width:280px;max-width:100%}
.ftoggle{display:none;font:bold 14px Arial,sans-serif;padding:8px 14px;border-radius:999px;border:1px solid var(--ink);background:var(--ink);color:var(--paper);cursor:pointer;white-space:nowrap}
.mrow{flex-wrap:nowrap}.mrow #q{flex:1;min-width:0}
@media(max-width:700px){.ftoggle{display:inline-block}#more{display:none}#more.open{display:block}}

input[type=search]{flex:1;min-width:160px}
.chip .c{font-weight:normal;opacity:.65;margin-left:2px}.chip.zero{opacity:.55}
#orgs{display:flex;flex-wrap:wrap;gap:6px}
.reset{background:none;border:0;color:var(--red);font:600 13px Arial,sans-serif;cursor:pointer;text-decoration:underline}
.summary{font-size:14px;margin:18px 0 4px}
.summary b{font-family:Georgia,serif;font-size:18px}
.group{font-family:Georgia,serif;font-size:22px;font-weight:bold;margin:26px 0 6px;padding-bottom:6px;border-bottom:2px solid var(--ink)}
.group small{font-family:Arial,sans-serif;font-size:12px;color:var(--slate);font-weight:normal;margin-left:8px}
.ev{background:#fff;border:1px solid var(--line);border-radius:6px;padding:14px 16px;margin:10px 0;display:grid;grid-template-columns:64px 1fr;gap:14px}
.d{text-align:center;border-right:1px solid var(--line);padding-right:10px}
.d .m{font-size:11px;letter-spacing:1px;text-transform:uppercase;color:var(--red);font-weight:bold}
.d .n{font-family:Georgia,serif;font-size:30px;font-weight:bold;line-height:1}
.d .w{font-size:11px;color:var(--slate)}
.d .r{font-size:10px;color:var(--slate);margin-top:3px}
.ev h3{font-family:Georgia,serif;font-size:18px;margin:0 0 2px;line-height:1.25}
.org{font-size:13px;font-weight:bold}.org span{color:var(--slate);font-weight:normal}
.meta,.note{font-size:13px;color:#3d3f3e;margin-top:4px}
.tags{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.tag{font-size:10px;letter-spacing:.5px;text-transform:uppercase;font-weight:bold;padding:3px 7px;border-radius:3px;background:var(--soft)}
.tag.cat{background:#212322;color:#F6F5F0}.tag.vet{background:#1f3a5f;color:#fff}.tag.car{background:#9B9576;color:#212322}.tag.city{background:#A72B2A;color:#fff}
.tag.flag{background:#FBEBEB;color:var(--red)}.tag.gold{background:#F3F1E6;color:#6f6a4f}
.src{font-size:12px;color:var(--slate);margin-top:6px}
.note-static{background:#fff;border-left:4px solid var(--red);padding:10px 14px;font-size:13px;margin:18px 0 0}
.empty{background:#fff;border:1px dashed var(--gold);border-radius:6px;padding:16px;color:var(--slate);margin:10px 0}
footer{font-size:11px;color:var(--slate);padding:26px 0 40px;margin-top:30px;border-top:1px solid var(--line)}
@media(max-width:560px){.panel{position:static}h1{font-size:38px}.ev{grid-template-columns:52px 1fr;gap:10px;padding:12px}.d .n{font-size:24px}.lbl{min-width:100%}}
@media print{.panel{position:static}.chip .c{font-weight:normal;opacity:.65;margin-left:2px}.chip.zero{opacity:.55}
#orgs{display:flex;flex-wrap:wrap;gap:6px}
.reset{display:none}}
</style></head>
<body>
<header><div class="wrap">
<div class="kicker">Richmond · Peninsula · Southside · Hampton Roads</div>
<h1>Community <i>Events</i></h1>
<p class="dek">A tool to help you get more engaged in your community. Divine Nine, veterans, hiring and city events across Central and Coastal Virginia, updated every week for the year ahead.</p>
<div class="asof">Calendar as of __ASOF__</div>
</div></header>

<div class="panel" id="panel" hidden><div class="wrap">
<div class="row"><span class="lbl">View</span><span id="views"></span>
  <select id="period" aria-label="Choose month or week"></select></div>
<div class="row mrow"><input type="search" id="q" placeholder="Search events, organizations, venues" aria-label="Search">
  <button class="ftoggle" id="ftoggle" type="button" aria-expanded="false" aria-controls="more">Filters <span id="fcount"></span></button></div>
<div id="more">
<div class="row"><span class="lbl">Community</span><span id="cats"></span></div>
<div class="row"><span class="lbl">Region</span><span id="regions"></span></div>
<div class="row"><span class="lbl">Org type</span><span id="otypes"></span></div>
<div class="row"><span class="lbl">Organization</span><select id="orgsel" aria-label="Organization"></select></div>
<div class="row"><span class="lbl">Access</span>
  <select id="access" aria-label="Who can attend">
    <option value="">All events</option><option value="Public">Open to the public</option><option value="Members">Members / brothers only</option><option value="Observance">Founders' Days</option></select>
  <button class="reset" id="reset" type="button">Reset</button></div>
</div>
</div></div>

<main class="wrap">
<div class="note-static" id="staticNote">Showing the full calendar. To use the filters (month, week, region, organization, search), download this file and open it in Chrome, Safari or Edge.</div>
<div class="summary" id="summary">__SUMMARY__</div>
<div id="list">__STATIC__</div>
</main>

<footer><div class="wrap">Every listing links to the host's own page; always confirm with the host before you go. "Check with host" means sources conflict; "Date TBC" means this year's date is not posted yet. To list an event, email kerry@blacklionret.com with the subject "Community Events submission". Community Events is an independent community calendar, not affiliated with or endorsed by the National Pan-Hellenic Council, its member organizations, the U.S. Department of Veterans Affairs, any veterans organization or any employer, workforce agency, city or event organizer listed. Presented by Black Lion Alliance · 13176 Jefferson Ave, Suite D, Newport News, VA 23608.</div></footer>

<script>
const EVENTS = __DATA__;
const START = '__W0__', END = '__W1__';
const REGIONS = ['All','Richmond','Peninsula','Southside','Region-wide'];
const VIEWS = [['all','Next 12 months'],['month','By month'],['week','By week']];
const P = s => { const [y,m,d] = s.split('-').map(Number); return new Date(Date.UTC(y,m-1,d)); };
const I = d => d.toISOString().slice(0,10);
const F = (d,o) => new Intl.DateTimeFormat('en-US',Object.assign({timeZone:'UTC'},o)).format(d);
const md = d => F(d,{month:'short',day:'numeric'});
const esc = s => String(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const add = (d,n) => { const x = new Date(d); x.setUTCDate(x.getUTCDate()+n); return x; };
const evEnd = e => e.end || e.start;
const overlaps = (e,a,b) => evEnd(e) >= a && e.start <= b;

const weeks = []; for (let w = P(START); I(w) <= END; w = add(w,7)) weeks.push([I(w), I(add(w,6))]);
const months = __MONTHS__;
const events = EVENTS.slice().sort((a,b)=>a.start.localeCompare(b.start)||a.title.localeCompare(b.title));
const ORGS = ['Alpha Phi Alpha','Alpha Kappa Alpha','Kappa Alpha Psi','Omega Psi Phi','Delta Sigma Theta','Phi Beta Sigma','Zeta Phi Beta','Sigma Gamma Rho','Iota Phi Theta'];
const OTYPES = ['Divine Nine','Veterans organizations','Government and agencies','Employers and workforce','Community and nonprofit'];
function otype(e){
  if (e.org_type) return e.org_type;
  const o = e.org||'';
  if (ORGS.includes(o)) return 'Divine Nine';
  if (/American Legion|VFW|\bDAV\b|Disabled American Veterans|AMVETS|Council of Veterans|Wreaths Across America|Military Order|Vietnam Veterans of America/i.test(o)) return 'Veterans organizations';
  if (/Virginia Works|Workforce|Career Works|Opportunity Center|Employment Center|RecruitMilitary/i.test(o)) return 'Employers and workforce';
  if (/^City of|County|Commission|Mayor|Department|Medical Center|\bVA\b|Virginia War Memorial|Virginia War Museum|Public Schools|Commonwealth|Parks and Recreation/i.test(o)) return 'Government and agencies';
  return 'Community and nonprofit';
}
const FAMS = [['American Legion','American Legion · all posts'],['VFW','VFW · all posts'],['DAV','DAV · all chapters'],['AMVETS','AMVETS · all posts']];
const orgMatch = (e,v) => v.startsWith('fam:') ? (e.org||'').startsWith(v.slice(4)) : e.org===v;

const CATS=[['All','All'],['D9','Divine Nine'],['Veterans','Veterans'],['Careers','Careers'],['City','City events']];
const CATN={D9:'Divine Nine',Veterans:'Veterans',Careers:'Careers',City:'City events'};
const CATC={D9:'cat',Veterans:'vet',Careers:'car',City:'city'};
const S = {view:'all', period:'', cat:'All', region:'All', otype:'All', org:'', access:'', q:''};
function todayISO(){ return new Intl.DateTimeFormat('en-CA',{timeZone:'America/New_York',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date()); }
function defaultWeek(){ const t = todayISO(); return (weeks.find(w=>w[0]<=t && t<=w[1]) || weeks[0])[0]; }
function defaultMonth(){ const t = todayISO(); return (months.find(m=>m[0]<=t && t<=m[1]) || months[0])[0]; }

function chips(el, items, key){
  el.innerHTML = items.map(([v,l])=>`<button class="chip" type="button" data-v="${v}">${l}</button>`).join(' ');
  el.addEventListener('click', ev => { const b = ev.target.closest('button'); if(!b) return; S[key] = b.dataset.v;
    if (key==='view') S.period = S.view==='week' ? defaultWeek() : S.view==='month' ? defaultMonth() : '';
    draw(); });
}
chips(document.getElementById('views'), VIEWS, 'view');
chips(document.getElementById('cats'), CATS, 'cat');
chips(document.getElementById('regions'), REGIONS.map(r=>[r,r]), 'region');
const otEl = document.getElementById('otypes');
otEl.addEventListener('click', ev => { const b = ev.target.closest('button'); if(!b) return; S.otype = b.dataset.v; S.org = ''; draw(); });
const orgSel = document.getElementById('orgsel'); orgSel.onchange = () => { S.org = orgSel.value; draw(); };
const accSel = document.getElementById('access'); accSel.onchange = () => { S.access = accSel.value; draw(); };
const q = document.getElementById('q'); q.oninput = () => { S.q = q.value.trim().toLowerCase(); draw(); };
const per = document.getElementById('period'); per.onchange = () => { S.period = per.value; draw(); };
const ft=document.getElementById('ftoggle'), more=document.getElementById('more');
ft.onclick=()=>{ const o=more.classList.toggle('open'); ft.setAttribute('aria-expanded',String(o)); };
document.getElementById('reset').onclick = () => { Object.assign(S,{view:'all',period:'',cat:'All',region:'All',otype:'All',org:'',access:'',q:''}); accSel.value=''; q.value=''; draw(); };

function passes(e){
  if (S.cat!=='All' && !(e.category||['D9']).includes(S.cat)) return false;
  if (S.region!=='All' && e.region!==S.region) return false;
  if (S.otype!=='All' && otype(e)!==S.otype) return false;
  if (S.org && !orgMatch(e,S.org)) return false;
  if (S.access==='Public' && e.access!=='Public') return false;
  if (S.access==='Members' && !(e.access==='Members'||e.access==='Brothers')) return false;
  if (S.access==='Observance' && e.access!=='Observance') return false;
  if (S.q){ const hay = [e.title,e.org,e.chapter,e.venue,e.address,e.note,e.region].join(' ').toLowerCase(); if (!hay.includes(S.q)) return false; }
  return true;
}
function card(e){
  const s=P(e.start), t=P(evEnd(e)), multi=e.start!==evEnd(e);
  const tags=(e.category||['D9']).map(c=>`<span class="tag ${CATC[c]||'cat'}">${CATN[c]||c}</span>`);
  tags.push(`<span class="tag">${esc(e.region)}</span>`);
  tags.push(e.access==='Members'?'<span class="tag gold">Members only</span>':e.access==='Brothers'?'<span class="tag gold">Brothers</span>':e.access==='Observance'?`<span class="tag gold">Founders' Day</span>`:'<span class="tag">Open to the public</span>');
  if (e.status && e.status!=='Confirmed') tags.push(`<span class="tag flag">${esc(e.status)}</span>`);
  const where=[e.venue,e.address].filter(Boolean).map(esc).join(' · ');
  const meta=[e.time?esc(e.time):'',where,e.cost?esc(e.cost):''].filter(Boolean).join(' · ');
  return `<article class="ev"><div class="d"><div class="m">${F(s,{month:'short'})}</div><div class="n">${F(s,{day:'numeric'})}</div><div class="w">${F(s,{weekday:'short'})}</div>${multi?`<div class="r">to ${md(t)}</div>`:''}</div>
  <div><h3>${esc(e.title)}</h3><div class="org">${esc(e.org)} <span>· ${esc(e.chapter)}</span></div>
  ${meta?`<div class="meta">${meta}</div>`:''}${e.note?`<div class="note">${esc(e.note)}</div>`:''}
  <div class="tags">${tags.join('')}</div>
  ${e.source_url?`<div class="src">Source: <a href="${esc(e.source_url)}" target="_blank" rel="noopener">${esc(e.source_label||'host page')}</a></div>`:(e.source_label?`<div class="src">Source: ${esc(e.source_label)}</div>`:'')}</div></article>`;
}
const empty = '<div class="empty">No listings match yet. Hosts: email kerry@blacklionret.com with the subject "Community Events submission".</div>';
function block(title, sub, items){ return `<div class="group">${esc(title)}<small>${sub}</small></div>` + (items.length ? items.map(card).join('') : empty); }
const n = k => `${k} listing${k===1?'':'s'}`;

function draw(){
  document.querySelectorAll('#views .chip').forEach(b=>b.setAttribute('aria-pressed', String(b.dataset.v===S.view)));
  document.querySelectorAll('#cats .chip').forEach(b=>b.setAttribute('aria-pressed', String(b.dataset.v===S.cat)));
  document.querySelectorAll('#regions .chip').forEach(b=>b.setAttribute('aria-pressed', String(b.dataset.v===S.region)));
  if (S.view==='all'){ per.hidden = true; }
  else {
    per.hidden = false;
    const opts = S.view==='month'
      ? [['', 'Every month']].concat(months.map(m=>[m[0], m[2]]))
      : [['', 'Every week']].concat(weeks.map((w,i)=>[w[0], `Week ${i+1} · ${md(P(w[0]))} to ${md(P(w[1]))}`]));
    per.innerHTML = opts.map(([v,l])=>`<option value="${v}">${l}</option>`).join('');
    per.value = S.period;
  }
  const inWin = e => overlaps(e,START,END);
  const cntT = t => events.filter(e=>{ const a=S.otype,b=S.org; S.otype=t; S.org=''; const r=passes(e)&&inWin(e); S.otype=a; S.org=b; return r; }).length;
  otEl.innerHTML = ['All'].concat(OTYPES).map(t=>{ const c=cntT(t); return `<button class="chip${c?'':' zero'}" type="button" data-v="${esc(t)}" aria-pressed="${S.otype===t}">${esc(t)} <span class="c">${c}</span></button>`; }).join(' ');
  const cntO = v => events.filter(e=>{ const b=S.org; S.org=v; const r=passes(e)&&inWin(e); S.org=b; return r; }).length;
  const winEv = events.filter(inWin);
  let opts = `<option value="">All organizations (${cntO('')})</option>`;
  (S.otype==='All'?OTYPES:[S.otype]).forEach(t=>{
    const names = t==='Divine Nine' ? ORGS : [...new Set(winEv.filter(e=>otype(e)===t).map(e=>e.org))].sort();
    const fams = FAMS.filter(([f])=>winEv.filter(e=>otype(e)===t && (e.org||'').startsWith(f)).length>1);
    if (!names.length) return;
    opts += `<optgroup label="${esc(t)}">` + fams.map(([f,l])=>`<option value="fam:${esc(f)}">${esc(l)} (${cntO('fam:'+f)})</option>`).join('') + names.map(o=>`<option value="${esc(o)}">${esc(o)} (${cntO(o)})</option>`).join('') + '</optgroup>';
  });
  orgSel.innerHTML = opts; orgSel.value = S.org;
  const pool = events.filter(passes);
  let html = '', count = 0, scope = '__SCOPE__';
  if (S.view==='all'){
    const items = pool.filter(e=>overlaps(e,START,END)); count = items.length;
    const later = [];
    months.forEach(m=>{ const it = items.filter(e=>e.start>=m[0] && e.start<=m[1]); if (it.length) html += block(m[2], n(it.length), it); else later.push(m[2]); });
    if (later.length) html += `<div class="empty">Nothing posted yet for ${esc(later.join(', '))}. Hosts usually announce events a few weeks out; this calendar is updated every Monday.</div>`;
  } else if (S.view==='month'){
    const list = S.period ? months.filter(m=>m[0]===S.period) : months;
    const seen = new Set();
    list.forEach(m=>{
      const it = pool.filter(e=>e.start>=m[0] && e.start<=m[1]); it.forEach(e=>seen.add(e.id));
      html += `<div class="group" style="border-bottom:4px solid var(--red)">${esc(m[2])}<small>${n(it.length)}</small></div>`;
      weeks.filter(w=>w[1]>=m[0] && w[0]<=m[1]).forEach(w=>{
        const wi = it.filter(e=>e.start>=w[0] && e.start<=w[1]);
        html += `<div style="font-weight:bold;font-size:13px;letter-spacing:1px;text-transform:uppercase;color:var(--gold);margin:16px 0 0">Week of ${md(P(w[0]))} to ${md(P(w[1]))}</div>` + (wi.length ? wi.map(card).join('') : '<div class="empty" style="padding:10px 14px">Nothing listed this week yet.</div>');
      });
    });
    count = seen.size; if (S.period) scope = list[0][2];
  } else {
    const list = S.period ? weeks.filter(w=>w[0]===S.period) : weeks;
    const seen = new Set();
    list.forEach(w=>{ const i = weeks.indexOf(w)+1; const it = pool.filter(e=>overlaps(e,w[0],w[1])); it.forEach(e=>seen.add(e.id));
      html += block(`Week ${i} · ${md(P(w[0]))} to ${md(P(w[1]))}`, n(it.length), it); });
    count = seen.size; if (S.period){ const w = list[0]; scope = `${md(P(w[0]))} to ${md(P(w[1]))}`; }
  }
  const active = [S.cat!=='All'?CATN[S.cat]:'', S.region!=='All'?S.region:'', S.otype!=='All'?S.otype:'', S.org.startsWith('fam:')?S.org.slice(4)+' (all posts)':S.org, S.access?accSel.options[accSel.selectedIndex].text:'', S.q?`"${S.q}"`:''].filter(Boolean).join(' · ');
  document.getElementById('summary').innerHTML = `<b>${n(count)}</b> · ${esc(scope)}${active?` · <span style="color:var(--red)">${esc(active)}</span>`:''}`;
  document.getElementById('list').innerHTML = html;
  const nf=[S.cat!=='All',S.region!=='All',S.otype!=='All',!!S.org,!!S.access].filter(Boolean).length; document.getElementById('fcount').textContent = nf?`(${nf})`:'';
}
document.getElementById("panel").hidden=false;document.getElementById("staticNote").style.display="none";
draw();
(function(){ if (window.parent===window) return; const ph=()=>parent.postMessage({ceHeight:document.documentElement.scrollHeight},'*'); new ResizeObserver(ph).observe(document.body); addEventListener('load',ph); ph(); })();
</script>
</body></html>'''


from datetime import date
E = html.escape
evs = sorted(data['events'], key=lambda x: (x['start'], x['title']))
def d(x): return date.fromisoformat(x)
def card(e):
    s, t = d(e['start']), d(e.get('end') or e['start'])
    tags = ['<span class="tag %s">%s</span>' % ({'Veterans':'vet','Careers':'car','City':'city'}.get(c,'cat'), {'Veterans':'Veterans','Careers':'Careers','City':'City events'}.get(c,'Divine Nine')) for c in e.get('category',['D9'])]
    tags.append(f'<span class="tag">{E(e["region"])}</span>')
    tags.append({'Members':'<span class="tag gold">Members only</span>','Brothers':'<span class="tag gold">Brothers</span>','Observance':"<span class=\"tag gold\">Founders' Day</span>"}.get(e['access'],'<span class="tag">Open to the public</span>'))
    if e.get('status') and e['status']!='Confirmed': tags.append(f'<span class="tag flag">{E(e["status"])}</span>')
    where = ' · '.join(E(v) for v in [e.get('venue'), e.get('address')] if v)
    meta = ' · '.join(v for v in [E(e.get('time') or ''), where, E(e.get('cost') or '')] if v)
    rng = f'<div class="r">to {t.strftime("%b")} {t.day}</div>' if s != t else ''
    src = f'<div class="src">Source: <a href="{E(e["source_url"])}" target="_blank" rel="noopener">{E(e.get("source_label") or "host page")}</a></div>' if e.get('source_url') else (f'<div class="src">Source: {E(e["source_label"])}</div>' if e.get('source_label') else '')
    return (f'<article class="ev"><div class="d"><div class="m">{s.strftime("%b")}</div><div class="n">{s.day}</div><div class="w">{s.strftime("%a")}</div>{rng}</div>'
            f'<div><h3>{E(e["title"])}</h3><div class="org">{E(e["org"])} <span>· {E(e["chapter"])}</span></div>'
            + (f'<div class="meta">{meta}</div>' if meta else '') + (f'<div class="note">{E(e["note"])}</div>' if e.get('note') else '')
            + f'<div class="tags">{"".join(tags)}</div>{src}</div></article>')
static = ''
for m0, m1, label in MONTHS:
    it = [e for e in evs if m0 <= e['start'] <= m1]
    if not it: continue
    static += f'<div class="group">{label}<small>{len(it)} listing{"" if len(it)==1 else "s"}</small></div>' + ''.join(card(e) for e in it)
evs = [e for e in evs if (e.get('end') or e['start']) >= W0.isoformat() and e['start'] <= W1.isoformat()]
summary = f'<b>{len(evs)} listings</b> · {SCOPE}'
print(TEMPLATE.replace('__DATA__', payload).replace('__ASOF__', html.escape(as_of)).replace('__STATIC__', static).replace('__SUMMARY__', summary).replace('__W0__', W0.isoformat()).replace('__W1__', W1.isoformat()).replace('__MONTHS__', json.dumps(MONTHS)).replace('__SCOPE__', SCOPE))
