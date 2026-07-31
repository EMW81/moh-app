# Reuse Guide — Quitters HQ code → Medal of Honor Stories Browser
Source: EMW81/quitters-hq `app/src/app_template.html` (2026-07-30, post-Meridian, 279-test build).
Paste this whole document into the new project's Claude as the starting context.

## 0. Architecture that transfers wholesale
Quitters HQ is a single self-contained HTML file: all CSS in design tokens, vanilla JS,
state as one JS object persisted to IndexedDB, full-list innerHTML re-render on every
filter change (fast to ~1–2k rows), zero external dependencies. For a static-JSON
read-only browser this simplifies further: `fetch('records.json')` once into memory;
IndexedDB is only needed for user prefs (saved views, theme). Keep the single-file
discipline — it made iteration speed possible.

## 1. Meridian design tokens (light + dark + print) — reusable as-is
Everything colors through CSS custom properties; a permanent test asserts zero raw hex
outside this block. Swap accent values to suit the MoH tone; keep the structure.
```css
  :root{
  /* type */
  --font-ui:"Geist",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --font-mono:"Geist Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  /* neutrals */
  --bg:#fafafa; --surface:#ffffff; --surface-raised:#f4f4f5;
  --border:#e4e4e7; --border-strong:#d4d4d8;
  --text:#18181b; --text-muted:#52525b; --text-subtle:#a1a1aa;
  /* rail — THEME-RESPONSIVE per the Claude mock (2026-07-30): light sidebar in light mode,
     dark sidebar in dark mode. Light values chain to existing neutrals; the dark values live
     in the [data-theme="dark"] block. (Supersedes the old dark-rail-in-both-modes note.) */
  --rail:var(--bg); --rail-raised:var(--surface-raised); --rail-border:var(--border);
  --rail-text:var(--text); --rail-muted:var(--text-muted); --rail-subtle:var(--text-subtle);
  --rail-hover:color-mix(in srgb,var(--text) 6%,transparent);
  --rail-inverse:#131316; --rail-inverse-text:#ededf0;   /* always-dark inverse chrome (toasts) */
  --rail-badge-ink:var(--rail-inverse);                  /* dark ink for badge text on the amber pill/youtag, both modes */
  /* accent (ONE) */
  --accent:#5b5bd6; --accent-solid:#5b5bd6; --accent-hover:#4f4fc8;
  --accent-pressed:#4646b8; --accent-bg:#eeeef8; --accent-fg:#ffffff;
  /* semantics — solid + -bg pair */
  --success:#188a4d;  --success-bg:#e7f4ed;
  --warning:#b45309;  --warning-bg:#f9efe2;
  --critical:#d92d20; --critical-bg:#fdecea;
  --info:#0369a1;     --info-bg:#e7f1f7;
  --gold:#a16207;     --gold-bg:#f7f0da;
  --violet:#7c3aed;   --violet-bg:#f1eafd;
  --neutral:#71717a;  --neutral-bg:#f0f0f1;
  /* geometry */
  --radius-sm:4px; --radius:6px; --radius-lg:8px; --radius-pill:999px;
  --shadow-sm:0 1px 2px rgba(0,0,0,.05);
  --shadow-md:0 1px 3px rgba(0,0,0,.07),0 4px 14px rgba(0,0,0,.05);
  --shadow-lg:0 4px 12px rgba(0,0,0,.10),0 12px 32px rgba(0,0,0,.12);
  --ring:0 0 0 3px rgba(91,91,214,.28);
  --ring-critical:0 0 0 3px rgba(217,45,32,.22);
  /* department ramp ×14 — thin bars + chips ONLY, never fills */
  --dept-props:#c2410c;        --dept-dressing:#a16207;
  --dept-construction:#92663d; --dept-graphics:#4d7c0f;
  --dept-greens:#15803d;       --dept-production:#64748b;
  --dept-ad:#0369a1;           --dept-locations:#0f766e;
  --dept-transpo:#155e75;      --dept-camera:#1d4ed8;
  --dept-stunts:#9f1239;       --dept-wardrobe:#a63a99;
  --dept-hair:#7c3aed;         --dept-makeup:#d1435b;
  /* bespoke canvas palette — frozen legacy surface colors, theme-invariant (spec §8: hex only in token defs) */
  --gold-d:#8a5a1e; --c-white:#fff; --c-black:#000; --c-gray-dash:#ccc; --c-paper-head:#faf7f1; --c-paper-field:#fcfbf7;
  --c-paper-panel:#fbfaf6; --c-paper-warm:#faf7ec; --c-paper-cat:#f7f5ef; --c-paper-canvas:#f4f1ea; --c-paper-mat:#efeadf; --c-paper-swatch:#f0ece2;
  --c-paper-tag:#eef0e9; --c-paper-msg:#eef2ec; --c-paper-msg2:#f6efe0; --c-paper-note:#fffdf6; --c-paper-hover:#f8f6f0; --c-paper-hover2:#faf8f2;
  --c-paper-chosen:#f0f7f1; --c-paper-moss:#e8f0ea; --c-paper-redbg:#fbe9e6; --c-paper-negbg:#fdf6f4; --c-paper-line:#eadfce; --c-paper-line2:#e0d8c8;
  --c-paper-line3:#ddd4c4; --c-paper-line4:#d8d0c2; --c-paper-border:#cfc8ba; --c-paper-borderd:#c3b9a5; --c-paper-grip:#c2b9a5; --c-paper-line5:#e7e2d6;
  --c-paper-track:#e9e6dc; --c-paper-rule:#efece3; --c-paper-item:#eee6d8; --c-paper-grid:#e2ddd0; --c-paper-negbd:#e3b7ad; --c-paper-muted:#8a7f6b;
  --c-paper-mutedx:#9a8f7c; --c-paper-mutedadd:#a99; --c-paper-body:#33302a; --c-paper-inkdark:#241d10; --c-paper-sbfoot:#2b1226; --c-paper-num:#7a5a2a;
  [data-theme="dark"]{
  --bg:#0f0f11; --surface:#161618; --surface-raised:#1f1f23;
  --border:#26262b; --border-strong:#313138;
  --text:#ededf0; --text-muted:#9d9da6; --text-subtle:#66666e;
  /* dark rail — unchanged from the original values (dark mode is visually byte-identical) */
  --rail:#131316; --rail-raised:#232329; --rail-border:#202024;
  --rail-text:#ededf0; --rail-muted:#9d9da6; --rail-subtle:#66666e;
  --rail-hover:rgba(255,255,255,.04);
  --accent:#7b83eb; --accent-solid:#5e5edd; --accent-hover:#6e76e8;
  --accent-pressed:#5252d0; --accent-bg:rgba(123,131,235,.14); --accent-fg:#ffffff;
  --success:#3fbf76;  --success-bg:rgba(63,191,118,.13);
  --warning:#e5a13c;  --warning-bg:rgba(229,161,60,.13);
  --critical:#f0655a; --critical-bg:rgba(240,101,90,.13);
  --info:#4db8f0;     --info-bg:rgba(77,184,240,.13);
  --gold:#d9b13b;     --gold-bg:rgba(217,177,59,.13);
  --violet:#a78bfa;   --violet-bg:rgba(167,139,250,.13);
  --neutral:#8f8f98;  --neutral-bg:rgba(143,143,152,.13);
  --shadow-sm:0 1px 2px rgba(0,0,0,.4);
  --shadow-md:0 1px 3px rgba(0,0,0,.5),0 4px 14px rgba(0,0,0,.35);
  --shadow-lg:0 4px 12px rgba(0,0,0,.5),0 16px 40px rgba(0,0,0,.5);
  --ring:0 0 0 3px rgba(123,131,235,.35);
  --dept-props:#fb923c;        --dept-dressing:#eab308;
  --dept-construction:#c99a6a; --dept-graphics:#a3cc4a;
  --dept-greens:#4ade80;       --dept-production:#94a3b8;
  --dept-ad:#4db8f0;           --dept-locations:#2dd4bf;
  --dept-transpo:#22d3ee;      --dept-camera:#60a5fa;
  --dept-stunts:#fb7185;       --dept-wardrobe:#d668c9;
  --dept-hair:#a78bfa;         --dept-makeup:#f472b6;
  }
  @media print{
  :root,[data-theme="dark"]{
    --bg:#ffffff; --surface:#ffffff; --surface-raised:#f4f4f5;
    --border:#d4d4d8; --border-strong:#a1a1aa;
    --text:#111113; --text-muted:#3f3f46; --text-subtle:#71717a;
    --shadow-sm:none; --shadow-md:none; --shadow-lg:none;
    /* dept ramp: keep LIGHT values (ink-weight, grayscale-distinguishable) */
  }
  *{-webkit-print-color-adjust:exact;print-color-adjust:exact;}
  .rail,nav.sidebar{display:none;}
  /* dept accent bars must survive: they are borders/backgrounds, exact-printed above */
  }
  *{box-sizing:border-box;margin:0;padding:0}
```
What to change: the `--dept-*` ramp becomes your 4 category-GROUP accents (use only as
thin bars/chips, never fills). Theme is applied via `data-theme="dark"` on `<html>`;
wire a 3-way Auto/Light/Dark control persisted in prefs.

## 2. The filter engine — your core reuse (multi-select, search, count bar, saved views)
This is the exact system for your filter panel. Mapping: `sets`→battle, `cats`→branch,
`statuses`→war, `hero`→survived/fallen (binary), plus add `tags` as one more array
dimension for the 32 thematic categories — `elToggleFilter` already handles any array
dimension generically. `special` shows how to do computed filters.
```js
function elSetSort(v){state.elSort=v;save();elApplyFilters()}
// scene-ref parse ("E1S12" → [1,12]) for first-appearance sort + episode-span tooltip
function elJs(s){return String(s==null?'':s).replace(/\\/g,'\\\\').replace(/'/g,"\\'")}
// toolbar multi-select toggles (keep the open <details> menu open → light re-render)
function elToggleFilter(dim,value){const f=elFstate();if(!Array.isArray(f[dim]))return;const i=f[dim].indexOf(value);if(i>=0)f[dim].splice(i,1);else f[dim].push(value);save();elApplyFilters()}
function elSetHero(v){elFstate().hero=v||'';save();elApplyFilters()}
function elSetZac(b){elFstate().zac=!!b;save();elApplyFilters()}
function elSetSpecial(v){elFstate().special=v||'';save();elApplyFilters()}
function elSetGroupBy(v){state.elGroupBy=EL_GROUPS.some(g=>g[0]===v)?v:'none';save();elApplyFilters()}
let elSearchTimer=null;
function elOnSearch(v){if(elSearchTimer)clearTimeout(elSearchTimer);const val=v;elSearchTimer=setTimeout(()=>{elSetSearch(val)},180)}
function elSetSearch(v){elFstate().search=v||'';save();elApplyFilters()}
// click-to-filter (row cells) — focus that dimension; full re-render (menus reflect it)
function elFilterSet(id){elFstate().sets=[id];save();renderElements()}
function elFilterCat(c){elFstate().cats=[c];save();renderElements()}
function elFilterEp(ep){epSelSet('elements',[+ep]);renderElements()}
function elFilterEpSpan(id){const e=elById(id);if(!e)return;epSelSet('elements',elEpisodesOf(e));renderElements()}
function elRemoveFilter(dim,value){const f=elFstate();if(Array.isArray(f[dim])){const i=f[dim].indexOf(value);if(i>=0)f[dim].splice(i,1)}save();renderElements()}
function elClearFilter(kind){
 const f=elFstate();const alias={set:'sets',cat:'cats',status:'statuses'};if(alias[kind])kind=alias[kind];
 if(kind==='sets')f.sets=[];else if(kind==='cats')f.cats=[];else if(kind==='statuses')f.statuses=[];
 else if(kind==='hero')f.hero='';else if(kind==='zac')f.zac=false;else if(kind==='search')f.search='';
 else if(kind==='special')f.special='';else if(kind==='ep')epSelAll('elements');
 save();renderElements();
}
function elClearAllFilters(){const f=elFstate();f.sets=[];f.cats=[];f.statuses=[];f.hero='';f.zac=false;f.search='';f.special='';epSelAll('elements');save();renderElements()}
function elActiveFilterChips(){
 const f=elFstate(),chips=[];
 f.sets.forEach(id=>{const s=state.sets.find(x=>x.id===id);chips.push(['sets',id,'Set: '+(s?s.name:id)])});
 f.cats.forEach(c=>chips.push(['cats',c,'Category: '+c]));
 f.statuses.forEach(s=>chips.push(['statuses',s,'Status: '+s]));
 if(f.hero)chips.push(['hero','',f.hero==='hero'?'Hero only':'Background only']);
 if(f.special==='overdue')chips.push(['special','','Overdue · undecided']);
 else if(f.special==='uncosted')chips.push(['special','','Uncosted (no options)']);
 if(f.zac)chips.push(['zac','','Elements for Zac']);
 if((f.search||'').trim())chips.push(['search','','Search: “'+f.search.trim()+'”']);
 if(epSelGet('elements').length)chips.push(['ep','',epSelLabel('elements')]);
 if(!chips.length)return '';
 return `<div class="epf-chips" style="margin:0 0 8px">${chips.map(c=>{const act=c[1]!==''?`elRemoveFilter('${c[0]}','${elJs(c[1])}')`:`elClearFilter('${c[0]}')`;return `<span class="epf-chip on" onclick="${act}" title="remove">${rpEsc(c[2])} <svg class=icon><use href=#i-x></use></svg></span>`}).join('')}<span class="epf-chip" onclick="elClearAllFilters()">Clear all</span></div>`;
}
/* ---------- saved views (user + seeded smart presets) ---------- */
function elViewConfig(){const f=elFstate();return {filters:{sets:f.sets.slice(),cats:f.cats.slice(),statuses:f.statuses.slice(),hero:f.hero,zac:f.zac,search:f.search,special:f.special},eps:epSelGet('elements'),groupBy:state.elGroupBy,sort:elSortKey()}}
function elViewSig(cfg){const fl=cfg.filters||{};return JSON.stringify({sets:(fl.sets||[]).slice().sort(),cats:(fl.cats||[]).slice().sort(),statuses:(fl.statuses||[]).slice().sort(),hero:fl.hero||'',zac:!!fl.zac,search:fl.search||'',special:fl.special||'',eps:(cfg.eps||[]).slice().sort((a,b)=>a-b),groupBy:cfg.groupBy||'none',sort:cfg.sort||'decideby'})}
function elApplyView(id){const v=(state.elViews||[]).find(x=>x.id===id);if(!v)return;const fl=v.filters||{},f=elFstate();f.sets=(fl.sets||[]).slice();f.cats=(fl.cats||[]).slice();f.statuses=(fl.statuses||[]).slice();f.hero=fl.hero||'';f.zac=!!fl.zac;f.search=fl.search||'';f.special=fl.special||'';epSelSet('elements',v.eps||[]);state.elGroupBy=EL_GROUPS.some(g=>g[0]===v.groupBy)?v.groupBy:'none';state.elSort=v.sort||'decideby';save();renderElements();toast('View: '+v.name)}
function elSaveView(){const inp=rpEl('el-viewname'),name=(inp&&inp.value||'').trim();if(!name){toastErr('Name the view first');return}const cfg=elViewConfig();const ex=(state.elViews||[]).find(v=>v.name.toLowerCase()===name.toLowerCase());if(ex){Object.assign(ex,cfg,{name})}else{if(!Array.isArray(state.elViews))state.elViews=[];state.elViews.push(Object.assign({id:'elv'+(state.nextId++),name},cfg))}if(inp)inp.value='';save();renderElements();toast(ex?'View updated: '+name:'View saved: '+name)}
function elDeleteView(id){const i=(state.elViews||[]).findIndex(v=>v.id===id);if(i<0)return;const nm=state.elViews[i].name;state.elViews.splice(i,1);save();renderElements();toast('View deleted: '+nm)}
function elPaintViews(){const box=rpEl('el-views');if(!box)return;const views=state.elViews||[];if(!views.length){box.innerHTML='<span class="xs mut">No saved views yet — set filters, name them below, and Save view.</span>';return}const sig=elViewSig(elViewConfig());box.innerHTML='<span class="xs mut" style="margin-right:2px">Views:</span>'+views.map(v=>{const on=elViewSig(v)===sig;return `<span class="el-viewchip ${on?'on':''}" onclick="elApplyView('${v.id}')" title="apply view">${v.preset?'<span class="vstar"><svg class=icon><use href=#i-star></use></svg></span>':''}${rpEsc(v.name)}<span class="vx" onclick="event.stopPropagation();elDeleteView('${v.id}')" title="delete view"><svg class=icon><use href=#i-x></use></svg></span></span>`}).join('')}
/* ---------- search matcher + highlight ---------- */
function elMatchesSearch(e,q){
 q=String(q||'').toLowerCase();if(!q)return true;
 const hay=[e.name||'',e.designReasoning||''];
 const sp=e.suggestedSpec||{};['era','material','color','condition','mount'].forEach(k=>hay.push(sp[k]||''));
 (e.evidence||[]).forEach(v=>hay.push(v.quote||''));
 (e.openQuestions||[]).forEach(qq=>{hay.push(qq.q||'');hay.push(qq.a||'')});
 (e.options||[]).forEach(o=>{hay.push(o.label||'');hay.push(o.rationale||'');const os=o.spec||{};Object.keys(os).forEach(k=>hay.push(os[k]||''))});
 return hay.join('\n').toLowerCase().indexOf(q)>=0;
}
function elHl(text,q){const esc=rpEsc(text==null?'':String(text));q=String(q||'').trim();if(!q)return esc;try{const re=new RegExp('('+q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','ig');return esc.replace(re,'<mark class="el-hl">$1</mark>')}catch(e){return esc}}
/* ---------- group-by ---------- */
let elCollapsed={};
function elWeekStart(dateStr){const d=new Date(dateStr+'T12:00:00');const dow=(d.getDay()+6)%7;d.setDate(d.getDate()-dow);return d.toISOString().slice(0,10)}
function elGroupOf(e,gb){
 if(gb==='set'){const s=e.setId&&state.sets.find(x=>x.id===e.setId);return {key:e.setId||'~none',label:s?s.name:'No set'}}
 if(gb==='category')return {key:e.category||'~none',label:e.category||'No category'};
 if(gb==='status')return {key:e.status||'~none',label:e.status||'No status'};
 if(gb==='episode'){const ep=elEarliestEp(e);return {key:ep==null?'~none':'E'+ep,label:ep==null?'No episode':'Episode '+ep}}
 if(gb==='decideweek'){const db=elDecideBy(e);if(!db)return {key:'~none',label:'No decide-by date'};const mon=elWeekStart(db);return {key:mon,label:'Week of '+fmtDate(mon)}}
 return {key:'all',label:'All'};
}
function elGroups(list,gb){const order=[],map={};list.forEach(e=>{const g=elGroupOf(e,gb);if(!map[g.key]){map[g.key]={key:g.key,label:g.label,items:[],cost:0};order.push(g.key)}map[g.key].items.push(e);map[g.key].cost+=elEffectiveCost(e)});return order.map(k=>map[k])}
function elToggleGroup(key){const k=state.elGroupBy+'::'+key;elCollapsed[k]=!elCollapsed[k];elRenderBody()}
/* ---------- send a category / bible to its department owner ---------- */
const EL_SEND_TARGETS={
 zac:{label:'Prop master',cats:['hero prop','hand prop'],defDept:'props',bible:'zac'},
 megan:{label:'Set decorator',cats:['set dressing','greens'],defDept:'dressing',bible:'megan'},
 graphics:{label:'Graphics',cats:['graphics/signage'],defDept:'graphics',bible:'zac'},
 transpo:{label:'Transportation',cats:['vehicle'],defDept:'transpo',bible:'zac'},
};
function elSendDeptId(target){const m=state.sendMap||{};return m[target]||(EL_SEND_TARGETS[target]&&EL_SEND_TARGETS[target].defDept)||'props'}
function elFiltered(){
 const f=elFstate();
 let list=state.elements.slice();
 if(f.zac){const z=new Set(elForZac().map(e=>e.id));list=list.filter(e=>z.has(e.id))}
 list=list.filter(e=>{const eps=elEpisodesOf(e);return !eps.length||eps.some(ep=>epSelMatch('elements',ep))});
 if(f.sets.length)list=list.filter(e=>f.sets.indexOf(e.setId)>=0);
 if(f.cats.length)list=list.filter(e=>f.cats.indexOf(e.category)>=0);
 if(f.statuses.length)list=list.filter(e=>f.statuses.indexOf(e.status)>=0);
 if(f.hero)list=list.filter(e=>e.heroOrBg===f.hero);
 if(f.special==='overdue')list=list.filter(e=>{if(e.decision)return false;const s=elDecideStatus(e);return s&&s.cls==='overdue'});
 else if(f.special==='uncosted')list=list.filter(e=>!(e.options||[]).length);
 const q=(f.search||'').trim();if(q)list=list.filter(e=>elMatchesSearch(e,q));
 list.sort(elCmp(elSortKey()));
 return list;
}
// populate the multi-select menus + their (n) summaries from filter state
function elFilterMenuData(dim){
 if(dim==='sets')return state.sets.map(s=>({v:s.id,label:s.name}));
 if(dim==='cats')return EL_CATEGORIES.map(c=>({v:c,label:c}));
 if(dim==='statuses')return EL_STATUSES.map(s=>({v:s,label:s}));
 return [];
}
function elRenderFilterMenus(){
 const f=elFstate();
 [['sets','el-list-set','el-sum-set'],['cats','el-list-cat','el-sum-cat'],['statuses','el-list-status','el-sum-status']].forEach(m=>{
  const dim=m[0],cur=f[dim]||[],box=rpEl(m[1]);
  if(box)box.innerHTML=elFilterMenuData(dim).map(it=>`<label><input type="checkbox" ${cur.indexOf(it.v)>=0?'checked':''} onchange="elToggleFilter('${dim}','${elJs(it.v)}')">${rpEsc(it.label)}</label>`).join('');
  const sum=rpEl(m[2]);if(sum)sum.textContent=cur.length?'('+cur.length+')':'';
 });
}
function elPaintFilterSummaries(){const f=elFstate();[['sets','el-sum-set'],['cats','el-sum-cat'],['statuses','el-sum-status']].forEach(m=>{const sum=rpEl(m[1]);if(sum)sum.textContent=(f[m[0]]||[]).length?'('+f[m[0]].length+')':''})}
// always-visible count bar (B5)
function elRenderCountBar(){
 const el=rpEl('el-count');if(!el)return;
 const list=elFiltered(),M=state.elements.length;
 let undecided=0,overdue=0,cost=0;
 list.forEach(e=>{if(!e.decision){undecided++;const s=elDecideStatus(e);if(s&&s.cls==='overdue')overdue++}cost+=elEffectiveCost(e)});
 el.innerHTML=`<b>${list.length}</b> shown of ${M} · <b>${undecided}</b> undecided · <span class="${overdue?'cw-over':''}"><b>${overdue}</b> overdue</span> · <b>${money(cost)}</b> projected (shown set)`;
}
function elRowHTML(e){
 const set=e.setId&&state.sets.find(s=>s.id===e.setId);const span=elEpSpan(e);const q=(elFstate().search||'').trim();
 return `<div class="el-cat el-row" onclick="elOpenDetail('${e.id}')">
    <div class="el-name"><b>${elHl(e.name,q)}</b>${e.quantityNote?`<span class="el-qty" title="${rpEsc(e.quantityNote)}"><svg class=icon><use href=#i-triangle-alert></use></svg> multiples</span>`:''}${e.propId?'<span class="el-qty" style="color:var(--accent)" title="linked to props tracker"><svg class=icon><use href=#i-link></use></svg></span>':''}</div>
    <div class="xs">${set?`<a class="el-link" onclick="event.stopPropagation();elFilterSet('${set.id}')">${rpEsc(set.name)}</a>`:'<span class="mut">—</span>'}</div>
    <div class="el-ep"><a class="el-link" onclick="event.stopPropagation();elFilterEpSpan('${e.id}')" title="${rpEsc(span.title)}">${rpEsc(span.short)}</a></div>
    <div><span class="el-chip ${e.heroOrBg}" onclick="event.stopPropagation();elSetHero('${e.heroOrBg}')" title="filter">${e.heroOrBg==='hero'?'HERO':'BG'}</span></div>
    <div class="xs"><a class="el-link" onclick="event.stopPropagation();elFilterCat('${elJs(e.category)}')">${rpEsc(e.category)}</a></div>
    <div><select class="el-statussel" onclick="event.stopPropagation()" onchange="elSetStatus('${e.id}',this.value)">${EL_STATUSES.map(s=>`<option ${e.status===s?'selected':''}>${s}</option>`).join('')}</select></div>
    <div class="xs" onclick="event.stopPropagation()">${elDecideBadge(e)||'<span class="mut">—</span>'}</div>
    <div class="el-cw">${e.continuityWeight}</div>
  </div>`;
}
function elRenderBody(){
 const body=rpEl('el-body');if(!body)return;
 if(!state.elements.length){body.innerHTML='<div class="empty">No elements yet. Elements are derived from the script — <a class="el-link" onclick="scrGoToPanel()">open the Scripts panel</a> to load the episodes; parsing, auditing, and extraction all run automatically in one pass.</div>';return}
 const list=elFiltered();
 const head='<div class="el-cat head"><div>Element</div><div>Set</div><div title="episode span (from scene refs)">EP</div><div>Hero/BG</div><div>Category</div><div>Status</div><div title="decide-by date">Decide-by</div><div title="continuity weight (scenes)">CW</div></div>';
 if(!list.length){body.innerHTML=head+'<div class="empty">No elements match these filters. <a class="el-link" onclick="elClearAllFilters()">Clear filters</a></div>';return}
```
Adaptation notes:
- `elFstate()` in Quitters returns a per-page filter object stored in state; for you it's
  one global `{tags:[],branch:[],war:[],battle:[],fate:'',search:''}`.
- **Per-option count badges** (your requirement, beyond what Quitters shows): Quitters'
  `(n)` summaries count *selections*, not results. For live result-counts per option,
  compute them in `elFilterMenuData` by running `elFiltered()` once per dimension with
  that dimension's own filter removed (standard faceted-count behavior — counts show
  "what you'd get", ~33 passes over 3,500 records is still instant).
- Search: 180ms debounce + `elMatchesSearch` over name/citation/attributes + `elHl`
  match highlighting — keep all three, they're proven.
- Saved views (`elViewConfig`/`elApplyView`/`elSaveView`) give you shareable presets
  ("Marines · WWII · Fallen") for free.

## 3. Feedback system — toast + loading + confirm (Universal Feedback Law)
Every action confirms within 150ms; errors persist longer and are tappable. Adopt
unchanged; add `#toast` div + the .toast CSS from the token file's component section.
```js
function toast(msg,kind){
 const t=$("#toast");if(!t)return;
 t.textContent=msg;t.className='toast show'+(kind==='err'?' err':kind==='load'?' load':'');
 t.onclick=kind==='err'?(()=>t.classList.remove('show')):null;
 if(toastTimer){clearTimeout(toastTimer);toastTimer=null}
 if(kind==='load')return; // persists until the next toast() call replaces it
 toastTimer=setTimeout(()=>t.classList.remove('show'),kind==='err'?6000:2200);
}
function toastErr(msg){toast(msg,'err')}
function toastLoad(msg){toast(msg,'load')}
// run an async action with loading → success/error feedback (Universal Feedback Law)
async function withFeedback(loadingMsg,fn,okMsg){
 toastLoad(loadingMsg);
 try{const r=await fn();toast(okMsg||'Done');return r}
 catch(e){toastErr((e&&e.message)?('<svg class=icon><use href=#i-triangle-alert></use></svg> '+e.message):'<svg class=icon><use href=#i-triangle-alert></use></svg> Something went wrong');throw e}
}
/* ---------- reliable copy: verified, with textarea + modal fallbacks ---------- */
async function hqCopy(text,okMsg){
 text=String(text==null?'':text);okMsg=okMsg||'Copied to clipboard';
 // 1) async Clipboard API (await = verification the write resolved)
 try{if(navigator.clipboard&&navigator.clipboard.writeText){await navigator.clipboard.writeText(text);toast(okMsg);return true}}catch(e){}
 // 2) hidden textarea + execCommand('copy') (boolean = verification)
 try{
  const ta=document.createElement('textarea');ta.value=text;ta.setAttribute('readonly','');
  ta.style.position='fixed';ta.style.top='-2000px';ta.style.opacity='0';
  document.body.appendChild(ta);ta.focus();ta.select();try{ta.setSelectionRange(0,text.length)}catch(e){}
  const ok=!!(document.execCommand&&document.execCommand('copy'));ta.remove();
  if(ok){toast(okMsg);return true}
 }catch(e){}
 // 3) guaranteed fallback: show the text for manual copy
 hqCopyModal(text);return false;
}
function hqCopyModal(text){
 const ta=$("#hq-copy-text");if(ta)ta.value=String(text==null?'':text);
 const bg=$("#hq-copy-bg");if(bg)bg.classList.add('show');
 toastErr('Auto-copy blocked here — select the text and copy manually');
}
function hqCopySelectAll(){const ta=$("#hq-copy-text");if(!ta)return;ta.focus();ta.select();try{ta.setSelectionRange(0,ta.value.length)}catch(e){}
 // last try at a programmatic copy now that it's user-gesture selected
 try{if(document.execCommand&&document.execCommand('copy'))toast('Copied to clipboard')}catch(e){}}
function hqCopyClose(){const bg=$("#hq-copy-bg");if(bg)bg.classList.remove('show')}
function appConfirm(msg,yesLabel){
 return new Promise(res=>{
  $("#modal-q").textContent=msg;
  const lbl=yesLabel||"Delete";$("#modal-yes").textContent=lbl;
  // destructive-confirm uses the destructive variant; other confirms use primary (§7)
  $("#modal-yes").className='btn '+(/delete|remove|reset|discard|wipe|undo/i.test(lbl)?'btn-d':'btn-p');
  const bg=$("#modal-bg");bg.classList.add("show");
  const done=v=>{bg.classList.remove("show");$("#modal-yes").onclick=null;$("#modal-no").onclick=null;bg.onclick=null;document.removeEventListener('keydown',esc);res(v)};
  const esc=e=>{if(e.key==='Escape')done(false)};
  $("#modal-yes").onclick=()=>done(true);
  $("#modal-no").onclick=()=>done(false);
  bg.onclick=e=>{if(e.target===bg)done(false)};        // backdrop-click close
  document.addEventListener('keydown',esc);            // Esc close (§7)
 });
}
// global Esc closes any open overlay/modal (§7 — behaviour addition where absent)
document.addEventListener('keydown',e=>{
 if(e.key!=='Escape')return;
```

## 4. Persistence (only for prefs in your case)
IndexedDB KV with localStorage fallback, debounced `save()` + synchronous `saveNow()`
for high-value writes. For MoH: persist only `{views, theme, lastFilters}`.
```js
function idbAvailable(){try{return typeof indexedDB!=='undefined'&&indexedDB}catch(e){return false}}
function idbOpen(){
 return new Promise((res)=>{
  if(_idbDB)return res(_idbDB);if(_idbTried&&!idbAvailable())return res(null);_idbTried=true;
  if(!idbAvailable())return res(null);
  try{const rq=indexedDB.open('crewhq',1);rq.onupgradeneeded=()=>{const db=rq.result;if(!db.objectStoreNames.contains('kv'))db.createObjectStore('kv')};rq.onsuccess=()=>{_idbDB=rq.result;res(_idbDB)};rq.onerror=()=>res(null);}catch(e){res(null)}
 });
}
function idbGet(key){return idbOpen().then(db=>db?new Promise((res)=>{try{const tx=db.transaction('kv','readonly'),rq=tx.objectStore('kv').get(key);rq.onsuccess=()=>res(rq.result!=null?{value:rq.result}:null);rq.onerror=()=>res(null)}catch(e){res(null)}}):null)}
function idbSet(key,val){return idbOpen().then(db=>db?new Promise((res,rej)=>{try{const tx=db.transaction('kv','readwrite');tx.objectStore('kv').put(val,key);tx.oncomplete=()=>res(true);tx.onerror=()=>rej(tx.error||new Error('idb write'));tx.onabort=()=>rej(tx.error||new Error('idb abort'))}catch(e){rej(e)}}):Promise.reject(new Error('no idb'))) }
// unified get: IDB first, then window.storage
async function storageGet(key){
 try{const r=await idbGet(key);if(r)return r}catch(e){}
 try{return await window.storage.get(key)}catch(e){return null}
}
// unified set: IDB primary (big quota) + mirror to window.storage (host bridge); tolerate mirror quota errors
async function storageSet(key,val){
 let idbOK=false,mirrorOK=false;
 try{await idbSet(key,val);idbOK=true}catch(e){}
 try{await window.storage.set(key,val);mirrorOK=true}catch(e){if(!idbOK)throw e}
 return idbOK||mirrorOK;
}

/* ---------- Anthropic API key: PROJECT-level, survives version bumps ----------
   The key lived inside per-season settings, so a version update, a store reshape,
   or a season/project switch could orphan it. It now lives at its own stable IDB
   path per project (quitters-pd-v1-apikey-<project>), independent of the store
   blob. Boot migrates any key found at a legacy path (in-store settings or an
   un-suffixed global path). state.settings.anthropicApiKey is kept only as a
   display mirror — hqGetApiKey() is the single source of truth. */
let hqApiKeyCache=null;
function hqApiKeyPath(pid){return 'quitters-pd-v1-apikey-'+(pid||(store&&store.current&&store.current.project)||'quitters')}
function hqGetApiKey(){return (hqApiKeyCache||'').trim()}
async function hqSetApiKey(key){
 key=(key||'').trim();hqApiKeyCache=key;
 try{await storageSet(hqApiKeyPath(),key)}catch(e){}
 if(state&&state.settings)state.settings.anthropicApiKey=key; // mirror for display/back-compat
 return key;
}
// find a key stranded at a legacy path: current settings, any season's settings, or the old global path
async function hqRecoverLegacyKey(){
 try{if(state&&state.settings&&(state.settings.anthropicApiKey||'').trim())return state.settings.anthropicApiKey.trim()}catch(e){}
 try{if(store&&store.projects)for(const pid in store.projects){const p=store.projects[pid];for(const sid in p.seasons){const k=p.seasons[sid].shared&&p.seasons[sid].shared.settings&&p.seasons[sid].shared.settings.anthropicApiKey;if(k&&String(k).trim())return String(k).trim()}}}catch(e){}
 try{const r=await storageGet('quitters-pd-v1-apikey');if(r&&(r.value||'').trim())return String(r.value).trim()}catch(e){}
 return '';
}
function save(){
 if(typeof hqMarkDirty==='function')hqMarkDirty(); // adaptive-snapshot: a data change starts the active clock
 if(saveTimer)clearTimeout(saveTimer);
 saveTimer=setTimeout(async()=>{
  stCommit();
  try{ await storageSet(STORE_KEY,JSON.stringify(store)); persistOK=true }
  catch(e){ persistOK=false; toast('Storage full — Export a backup now (Settings)'); }
  paintSaveTag();
 },400);
}
// Durable write in the SAME tick (no debounce): commits state→store and awaits the
// storage write. Returns true on success, false if it failed (storage full/blocked).
// Use after high-value writes (paid AI output) so nothing is lost to the debounce
// window or a silent eviction. hqMarkDirty keeps the snapshot cadence honest.
async function saveNow(){
 if(typeof hqMarkDirty==='function')hqMarkDirty();
 if(saveTimer){clearTimeout(saveTimer);saveTimer=null}
 stCommit();
 try{ await storageSet(STORE_KEY,JSON.stringify(store)); persistOK=true; paintSaveTag(); return true; }
 catch(e){ persistOK=false; paintSaveTag(); return false; }
}
function paintSaveTag(){
 const el=$("#save-tag");if(!el)return;
 if(persistOK){el.classList.remove('warn');el.innerHTML='<svg class=icon><use href=#i-check></use></svg> Saving automatically';el.title=(idbAvailable()?'IndexedDB':'Local')+' storage · persists between sessions.'}
 else{el.classList.add('warn');el.innerHTML='<svg class=icon><use href=#i-triangle-alert></use></svg> Memory-only mode';el.title='Storage unavailable here — use Export in Settings to keep a backup.'}
}
/* ---------- header context switcher: one breadcrumb → one popover ---------- */
let hqDeptView='art';
// update the collapsed breadcrumb "Quitters · S1 · Art Dept"
function hqRenderAccordion(){
 if(!store)return;const c=store.current,proj=store.projects[c.project];
 const crumb=$("#hq-ctx-crumb");
 if(crumb)crumb.textContent=`${proj.name} · ${hqSeasonShort(proj.seasons[c.season].name)}`;
}
function hqTogglePopover(e){if(e)e.stopPropagation();const ov=$("#hqp-overlay");if(ov.classList.contains('open'))hqClosePopover();else hqOpenPopover()}
```

## 5. Row/card rendering + detail view pattern
Quitters renders table rows via template strings with `onclick="elOpenDetail(id)"`
opening a modal; you want a **card grid** — same pipeline, different template: 
`elRenderBody()` → build one HTML string → single innerHTML assignment. For photos at
3,500 records use `<img loading="lazy" decoding="async">` and render in chunks of ~200
via requestAnimationFrame if scroll jank appears. Escaping helpers (mandatory — citation
text will contain quotes/angle brackets):
```js
function elMatchesSearch(e,q){
 q=String(q||'').toLowerCase();if(!q)return true;
 const hay=[e.name||'',e.designReasoning||''];
 const sp=e.suggestedSpec||{};['era','material','color','condition','mount'].forEach(k=>hay.push(sp[k]||''));
 (e.evidence||[]).forEach(v=>hay.push(v.quote||''));
 (e.openQuestions||[]).forEach(qq=>{hay.push(qq.q||'');hay.push(qq.a||'')});
 (e.options||[]).forEach(o=>{hay.push(o.label||'');hay.push(o.rationale||'');const os=o.spec||{};Object.keys(os).forEach(k=>hay.push(os[k]||''))});
 return hay.join('\n').toLowerCase().indexOf(q)>=0;
}
function elHl(text,q){const esc=rpEsc(text==null?'':String(text));q=String(q||'').trim();if(!q)return esc;try{const re=new RegExp('('+q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','ig');return esc.replace(re,'<mark class="el-hl">$1</mark>')}catch(e){return esc}}
/* ---------- group-by ---------- */
let elCollapsed={};
function elWeekStart(dateStr){const d=new Date(dateStr+'T12:00:00');const dow=(d.getDay()+6)%7;d.setDate(d.getDate()-dow);return d.toISOString().slice(0,10)}
function rpEsc(s){return (s||'').replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;')}
function rpRoom(){return (state.rooms||[]).find(r=>r.id===rpActive)||null}
```
Detail view: keep it a modal over the grid (Quitters' `elOpenDetail` pattern) so filter
state survives; browser back-button support = one `history.pushState` on open.

## 6. Lessons learned the hard way (July 2026, in blood)
1. **IndexedDB, never localStorage, and export buttons that produce real files.** Chrome
   evicted our localStorage under disk pressure and we lost a day's data. Even for
   "just prefs," failure must be loud.
2. **No silent anything.** Every button: hover state, pressed state, result toast.
   A silent success is indistinguishable from a dead button (we shipped that bug; the
   user found it in minutes).
3. **Feed the machine documents, not formats.** Our biggest UX failure was making the
   user convert/import/reconcile. One door, one action, one clear done-state. For you:
   the JSON is the door; make loading states and record counts visible on boot.
4. **Derivation must be idempotent** — applies if you ever add AI enrichment (e.g.
   auto-tagging citations): fingerprint inputs, never re-run unchanged, never overwrite
   human edits (per-field manual flags).
5. **Full re-render is fine longer than you think** — but it died for us only because we
   stayed under ~2k rows visible. At 3,500 cards with images: lazy-load images, chunked
   render, and test on a phone early. Quitters is desktop-first and we regret not
   testing mobile continuously; your browser sounds public-facing — go mobile-first.
6. **Tokens-only color + a test that greps for raw hex.** Made a full restyle a
   one-evening job (307 hex values → 0) instead of a rewrite.
7. **Natural-sort filenames and escape everything.** Real data contains apostrophes
   (O'Hare), quotes, and ampersands; `rpEsc`/`elJs` everywhere or you'll ship XSS-shaped
   rendering bugs.
8. **Print/export styles from day one** if teachers/veterans' groups will print pages:
   we force light theme + exact colors under `@media print` at the token level.
