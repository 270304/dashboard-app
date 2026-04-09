"""
app.py — Team Productivity Dashboard (Streamlit)
Run: streamlit run app.py
"""
import time
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
import streamlit as st

import backend as db

st.set_page_config(
    page_title="Team Productivity",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.init_db()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* ── palette ── */
:root {
  --indigo:      #4F46E5;
  --indigo-light:#EEF2FF;
  --indigo-mid:  #C7D2FE;
  --indigo-dark: #3730A3;
  --violet:      #7C3AED;
  --violet-light:#F5F3FF;
  --violet-mid:  #DDD6FE;
  --blue:        #2563EB;
  --blue-light:  #EFF6FF;
  --blue-mid:    #BFDBFE;
  --blue-dark:   #1E40AF;
  --teal:        #0D9488;
  --teal-light:  #F0FDFA;
  --teal-mid:    #99F6E4;
  --teal-dark:   #115E59;
  --green:       #16A34A;
  --green-light: #F0FDF4;
  --green-mid:   #BBF7D0;
  --green-dark:  #14532D;
  --amber:       #D97706;
  --amber-light: #FFFBEB;
  --amber-mid:   #FDE68A;
  --amber-dark:  #78350F;
  --rose:        #E11D48;
  --rose-light:  #FFF1F2;
  --rose-mid:    #FECDD3;
  --rose-dark:   #881337;
  --surface:     #F8FAFC;
  --surface-2:   #F1F5F9;
  --border:      #E2E8F0;
  --border-d:    #CBD5E1;
  --text-1:      #0F172A;
  --text-2:      #334155;
  --text-3:      #64748B;
  --text-4:      #94A3B8;
  --r-s:6px; --r-m:10px; --r-l:14px; --r-xl:20px;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 100% !important; }

/* ══════════════ SIDEBAR ══════════════ */
[data-testid="stSidebar"] {
  background: linear-gradient(175deg, #1e1b4b 0%, #312e81 40%, #4338ca 100%);
  border-right: none;
}
[data-testid="stSidebar"] > div { padding: 1.5rem 1.25rem; }

.sb-brand {
  display: flex; align-items: center; gap: 10px;
  padding-bottom: 1.25rem; border-bottom: 1px solid rgba(255,255,255,.12);
  margin-bottom: 1.25rem;
}
.sb-icon {
  width: 36px; height: 36px; border-radius: 10px;
  background: rgba(255,255,255,.18); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; flex-shrink: 0;
}
.sb-title { font-size: 14px; font-weight: 700; color: #fff; letter-spacing: -.2px; }
.sb-sub   { font-size: 11px; color: rgba(255,255,255,.55); margin-top: 1px; }

.sb-section {
  font-size: 10px; font-weight: 600; letter-spacing: 1px;
  text-transform: uppercase; color: rgba(255,255,255,.4);
  margin: 1.25rem 0 .65rem;
}

.smcard {
  display: flex; align-items: center; gap: 10px; padding: 9px 10px;
  border-radius: var(--r-m); border: 1px solid transparent;
  margin-bottom: 4px; cursor: pointer; transition: background .12s;
}
.smcard:hover   { background: rgba(255,255,255,.08); }
.smcard.active  { background: rgba(255,255,255,.15); border-color: rgba(255,255,255,.25); }
.savatar {
  width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700;
}
.sname  { font-size: 13px; font-weight: 500; color: #fff; }
.srole  { font-size: 11px; color: rgba(255,255,255,.5); }
.sbadge {
  margin-left: auto; font-size: 11px; font-weight: 600; padding: 3px 9px;
  border-radius: 20px; white-space: nowrap;
  background: rgba(255,255,255,.12); color: rgba(255,255,255,.8);
}
.smcard.active .sbadge { background: rgba(255,255,255,.25); color: #fff; }

/* ══════════════ PAGE HEADER ══════════════ */
.pg-header {
  display: flex; align-items: flex-end; justify-content: space-between;
  margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid var(--indigo-mid);
}
.pg-title { font-size: 22px; font-weight: 700; color: var(--text-1); letter-spacing: -.4px; }
.pg-sub   { font-size: 13px; color: var(--text-3); margin-top: 3px; }
.pg-badge {
  font-size: 12px; font-weight: 600; padding: 5px 14px;
  border-radius: 20px; background: var(--indigo-light); color: var(--indigo-dark);
  border: 1px solid var(--indigo-mid);
}

/* ══════════════ METRIC CARDS ══════════════ */
.mg { display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-bottom: 2rem; }

.mc2 {
  border-radius: var(--r-l); padding: 1.25rem 1.4rem;
  position: relative; overflow: hidden; border: 1px solid transparent;
}
.mc2.indigo { background: linear-gradient(135deg, #4F46E5 0%, #6366f1 100%); }
.mc2.blue   { background: linear-gradient(135deg, #2563EB 0%, #3b82f6 100%); }
.mc2.teal   { background: linear-gradient(135deg, #0D9488 0%, #14b8a6 100%); }
.mc2.amber  { background: linear-gradient(135deg, #D97706 0%, #f59e0b 100%); }

.mc2 .lbl { font-size: 11px; font-weight: 600; letter-spacing: .4px;
            text-transform: uppercase; color: rgba(255,255,255,.7); margin-bottom: 8px; }
.mc2 .val { font-size: 32px; font-weight: 700; color: #fff;
            letter-spacing: -.8px; line-height: 1; }
.mc2 .sub { font-size: 12px; color: rgba(255,255,255,.65); margin-top: 6px; }
.mc2 .mc-icon {
  position: absolute; right: 16px; top: 50%; transform: translateY(-50%);
  font-size: 28px; opacity: .22;
}

/* ══════════════ SECTION HEADING ══════════════ */
.sh {
  font-size: 13px; font-weight: 700; color: var(--text-1); letter-spacing: -.1px;
  margin: 1.75rem 0 .85rem; display: flex; align-items: center; gap: 10px;
}
.sh .sh-dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.sh::after { content:''; flex:1; height:1px; background: var(--border); }

/* ══════════════ BAR ROWS ══════════════ */
.br { display:flex; align-items:center; gap:12px; margin-bottom:10px; }
.bn { font-size:13px; color:var(--text-2); width:80px; flex-shrink:0;
      overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.bn.bold { font-weight:700; color:var(--text-1); }
.bs { flex:1; display:flex; flex-direction:column; gap:4px; }
.bt { height:7px; background:var(--surface-2); border-radius:4px; overflow:hidden; }
.bf { height:100%; border-radius:4px; }
.bv { font-size:12px; color:var(--text-2); font-weight:600; width:38px; text-align:right; }

.legend { display:flex; gap:18px; font-size:12px; color:var(--text-3); margin-top:12px; align-items:center; }
.ldot   { display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:5px; vertical-align:middle; }

/* ══════════════ TIMER CARD ══════════════ */
.tc {
  border-radius: var(--r-xl); padding: 1.4rem 1.5rem;
  margin-bottom: 1.1rem; border: 1px solid var(--border);
  transition: box-shadow .15s;
}
.tc.work-mode  { background: linear-gradient(135deg, #EFF6FF 0%, #EEF2FF 100%);
                  border-color: var(--blue-mid); }
.tc.study-mode { background: linear-gradient(135deg, #F0FDF4 0%, #ECFDF5 100%);
                  border-color: var(--teal-mid); }
.tc.idle-mode  { background: #fff; border-color: var(--border); }

.tc-hdr { display:flex; align-items:center; gap:10px; margin-bottom:.85rem; }
.tc-av  {
  width:40px; height:40px; border-radius:50%; flex-shrink:0;
  display:flex; align-items:center; justify-content:center;
  font-size:13px; font-weight:700;
  box-shadow: 0 0 0 3px rgba(255,255,255,.8);
}
.tc-nm { font-size:14px; font-weight:700; color:var(--text-1); }
.tc-rl { font-size:12px; color:var(--text-3); }
.running-dot {
  width:9px; height:9px; border-radius:50%; background:#16A34A; margin-left:auto;
  box-shadow: 0 0 0 3px rgba(22,163,74,.25);
  animation: pulse 1.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(.82)} }

.timer-digits {
  font-family:'JetBrains Mono',monospace; font-size:46px; font-weight:500;
  text-align:center; letter-spacing:3px; padding:8px 0; line-height:1;
}
.timer-digits.work-color  { color: var(--blue); }
.timer-digits.study-color { color: var(--teal); }
.timer-digits.idle-color  { color: var(--text-3); }

.timer-st {
  text-align:center; font-size:12px; height:18px; margin-bottom:10px;
  font-weight: 500;
}
.timer-st.running { color: var(--green); }
.timer-st.paused  { color: var(--amber); }
.timer-st.idle    { color: var(--text-4); }

/* ══════════════ TASK ROWS ══════════════ */
.trow {
  display:flex; align-items:center; gap:8px; padding:9px 13px;
  background:#fff; border:1px solid var(--border);
  border-radius:var(--r-m); margin-bottom:5px;
  transition: border-color .1s, box-shadow .1s;
}
.trow:hover { border-color: var(--indigo); box-shadow: 0 0 0 2px var(--indigo-light); }
.ttxt { font-size:13px; color:var(--text-1); flex:1; }
.ttxt.done { text-decoration:line-through; color:var(--text-4); }

.tbadge { font-size:10px; font-weight:700; padding:3px 9px; border-radius:20px; letter-spacing:.2px; }
.tb-w { background: var(--blue-light);  color: var(--blue-dark);
        border: 1px solid var(--blue-mid); }
.tb-s { background: var(--teal-light);  color: var(--teal-dark);
        border: 1px solid var(--teal-mid); }

/* ══════════════ TEAM CARDS ══════════════ */
.tmcard {
  border-radius: var(--r-l); padding: 1.4rem 1rem; text-align: center;
  margin-bottom: 10px; border: 1px solid var(--border); background: #fff;
  transition: box-shadow .15s, transform .15s;
}
.tmcard:hover { box-shadow: 0 4px 20px rgba(79,70,229,.1); transform: translateY(-2px); }
.tm-av {
  width: 56px; height: 56px; border-radius: 50%; margin: 0 auto 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: 700;
  box-shadow: 0 0 0 4px rgba(255,255,255,1), 0 0 0 6px rgba(79,70,229,.2);
}
.tm-nm { font-size:14px; font-weight:700; color:var(--text-1); }
.tm-rl { font-size:12px; color:var(--text-3); margin-top:2px; }

/* ══════════════ SWATCHES ══════════════ */
.swatches { display:flex; gap:7px; flex-wrap:wrap; margin:6px 0 14px; }
.swatch { width:26px; height:26px; border-radius:50%; cursor:pointer;
          border:2px solid transparent; transition:transform .1s; }
.swatch.sel { transform:scale(1.4); border-color:#334155; }

/* ══════════════ STATS PILL ══════════════ */
.stat-pill {
  display:inline-flex; align-items:center; gap:6px;
  padding:5px 12px; border-radius:20px; font-size:12px; font-weight:600;
}
.sp-blue   { background:var(--blue-light);   color:var(--blue-dark);   border:1px solid var(--blue-mid);  }
.sp-teal   { background:var(--teal-light);   color:var(--teal-dark);   border:1px solid var(--teal-mid);  }
.sp-indigo { background:var(--indigo-light); color:var(--indigo-dark); border:1px solid var(--indigo-mid);}
.sp-amber  { background:var(--amber-light);  color:var(--amber-dark);  border:1px solid var(--amber-mid); }

@media(max-width:768px){
  .mg { grid-template-columns:1fr 1fr; }
  .timer-digits { font-size:34px; }
}
</style>
""", unsafe_allow_html=True)

# ── session state ─────────────────────────────────────────────────────────────
def _init():
    for k, v in {"active_member_id": None, "view": "today", "timers": {}, "selected_color": 0}.items():
        if k not in st.session_state:
            st.session_state[k] = v
_init()

members = db.get_members()
if not members:
    st.error("No members found. Check your database."); st.stop()
if st.session_state.active_member_id not in [m["id"] for m in members]:
    st.session_state.active_member_id = members[0]["id"]

# ── helpers ───────────────────────────────────────────────────────────────────
def ini(name): return "".join(w[0] for w in name.split())[:2].upper()
def gc(m):     return db.AVATAR_COLORS[m["color_idx"] % len(db.AVATAR_COLORS)]

def fmt(s):
    h, r = divmod(s, 3600); m, sc = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{sc:02d}"

def elapsed(mid):
    t = st.session_state.timers.get(mid, {})
    base = t.get("seconds", 0)
    if t.get("running") and t.get("start_ts"):
        base += int(time.time() - t["start_ts"])
    return base

def get_am():
    mid = st.session_state.active_member_id
    return next((m for m in members if m["id"] == mid), members[0])

def vl(): return "today" if st.session_state.view == "today" else "month"

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sb-brand">
      <div class="sb-icon">📊</div>
      <div><div class="sb-title">Team Productivity</div><div class="sb-sub">Dashboard</div></div>
    </div>""", unsafe_allow_html=True)

    vc = st.radio("Range", ["Today", "This Month"],
                  index=0 if st.session_state.view == "today" else 1, horizontal=True)
    st.session_state.view = "today" if vc == "Today" else "month"

    st.markdown('<div class="sb-section">Members</div>', unsafe_allow_html=True)
    for m in members:
        tot = round(db.sum_hours(m["id"], "company", vl()) + db.sum_hours(m["id"], "education", vl()), 1)
        act = "active" if m["id"] == st.session_state.active_member_id else ""
        c   = gc(m)
        st.markdown(f"""
<div class="smcard {act}">
  <div class="savatar" style="background:{c['bg']};color:{c['fg']}">{ini(m['name'])}</div>
  <div><div class="sname">{m['name']}</div><div class="srole">{m['role']}</div></div>
  <div class="sbadge">{tot}h</div>
</div>""", unsafe_allow_html=True)
        if st.button("Select", key=f"sel_{m['id']}", use_container_width=True,
                     type="primary" if m["id"] == st.session_state.active_member_id else "secondary"):
            st.session_state.active_member_id = m["id"]; st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
am        = get_am()
today_str = date.today().strftime("%A, %d %B %Y")
vs        = "Today" if vl() == "today" else "This Month"

st.markdown(f"""
<div class="pg-header">
  <div>
    <div class="pg-title">Good day, {am['name'].split()[0]} 👋</div>
    <div class="pg-sub">{today_str}</div>
  </div>
  <div class="pg-badge">{vs}</div>
</div>""", unsafe_allow_html=True)

tab_ov, tab_tr, tab_gr, tab_tm = st.tabs(["Overview", "Time Tracker", "Analytics", "Team"])

# ═══════════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tab_ov:
    ch   = db.sum_hours(am["id"], "company",   vl())
    sh   = db.sum_hours(am["id"], "education", vl())
    th   = round(ch + sh, 2)
    tsks = db.get_tasks(am["id"])
    dt   = sum(1 for t in tsks if t["done"])
    tt   = len(tsks)
    tpct = round(dt / tt * 100) if tt else 0
    tgt  = 8 if vl() == "today" else 160

    st.markdown(f"""
<div class="mg">
  <div class="mc2 indigo">
    <div class="lbl">Total Hours</div>
    <div class="val">{th}h</div>
    <div class="sub">of {tgt}h target</div>
    <div class="mc-icon">⏱</div>
  </div>
  <div class="mc2 blue">
    <div class="lbl">Work Hours</div>
    <div class="val">{ch}h</div>
    <div class="sub">company time</div>
    <div class="mc-icon">💼</div>
  </div>
  <div class="mc2 teal">
    <div class="lbl">Study Hours</div>
    <div class="val">{sh}h</div>
    <div class="sub">learning &amp; education</div>
    <div class="mc-icon">📚</div>
  </div>
  <div class="mc2 amber">
    <div class="lbl">Tasks Done</div>
    <div class="val">{dt}/{tt}</div>
    <div class="sub">{tpct}% completion rate</div>
    <div class="mc-icon">✅</div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="sh"><span class="sh-dot" style="background:#4F46E5"></span>Team hours breakdown</div>', unsafe_allow_html=True)
    st.caption(f"Target {tgt}h / {'day' if vl() == 'today' else 'month'}")

    for m in members:
        mc   = db.sum_hours(m["id"], "company",   vl())
        ms   = db.sum_hours(m["id"], "education", vl())
        tot  = round(mc + ms, 2)
        cpct = min(100, round(mc / tgt * 100)) if tgt else 0
        spct = min(100, round(ms / tgt * 100)) if tgt else 0
        bold = "bold" if m["id"] == am["id"] else ""
        st.markdown(f"""
<div class="br">
  <div class="bn {bold}">{m['name']}</div>
  <div class="bs">
    <div class="bt"><div class="bf" style="width:{cpct}%;background:linear-gradient(90deg,#2563EB,#6366f1)"></div></div>
    <div class="bt"><div class="bf" style="width:{spct}%;background:linear-gradient(90deg,#0D9488,#14b8a6)"></div></div>
  </div>
  <div class="bv">{tot}h</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div class="legend">
  <span><span class="ldot" style="background:#2563EB"></span>Work</span>
  <span><span class="ldot" style="background:#0D9488"></span>Study</span>
</div>""", unsafe_allow_html=True)

    st.markdown(f'<div class="sh"><span class="sh-dot" style="background:#D97706"></span>Tasks — {am["name"]}</div>', unsafe_allow_html=True)
    if not tsks:
        st.caption("No tasks yet. Add some in the Time Tracker tab.")
    else:
        for task in tsks:
            dc = "done" if task["done"] else ""
            bc = "tb-w" if task["task_type"] == "company" else "tb-s"
            bl = "work" if task["task_type"] == "company" else "study"
            st.markdown(f"""
<div class="trow">
  <span class="ttxt {dc}">{task['name']}</span>
  <span class="tbadge {bc}">{bl}</span>
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TIME TRACKER
# ═══════════════════════════════════════════════════════════════════════════════
with tab_tr:
    lc, rc = st.columns([3, 2], gap="large")

    with lc:
        st.markdown('<div class="sh"><span class="sh-dot" style="background:#2563EB"></span>Timers</div>', unsafe_allow_html=True)

        for m in members:
            mid = m["id"]
            if mid not in st.session_state.timers:
                st.session_state.timers[mid] = {"running": False, "seconds": 0, "type": "company", "start_ts": None}
            ts  = st.session_state.timers[mid]
            el  = elapsed(mid)
            cm  = gc(m)
            iw  = ts["type"] == "company"

            if ts["running"]:
                card_cls  = "work-mode" if iw else "study-mode"
                digit_cls = "work-color" if iw else "study-color"
                st_cls, st_txt = "running", "● Running"
            elif el > 0:
                card_cls  = "idle-mode"
                digit_cls = "work-color" if iw else "study-color"
                st_cls, st_txt = "paused", f"⏸ Paused at {fmt(el)}"
            else:
                card_cls  = "idle-mode"
                digit_cls = "idle-color"
                st_cls, st_txt = "idle", ""

            rdot = '<div class="running-dot"></div>' if ts["running"] else ""

            st.markdown(f"""
<div class="tc {card_cls}">
  <div class="tc-hdr">
    <div class="tc-av" style="background:{cm['bg']};color:{cm['fg']}">{ini(m['name'])}</div>
    <div><div class="tc-nm">{m['name']}</div><div class="tc-rl">{m['role']}</div></div>
    {rdot}
  </div>
</div>""", unsafe_allow_html=True)

            tt1, tt2 = st.columns(2)
            with tt1:
                if st.button("💼 Work",  key=f"tw_{mid}", use_container_width=True,
                             type="primary" if iw else "secondary", disabled=ts["running"]):
                    st.session_state.timers[mid]["type"] = "company"; st.rerun()
            with tt2:
                if st.button("📚 Study", key=f"ts_{mid}", use_container_width=True,
                             type="primary" if not iw else "secondary", disabled=ts["running"]):
                    st.session_state.timers[mid]["type"] = "education"; st.rerun()

            st.markdown(f'<div class="timer-digits {digit_cls}">{fmt(el)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="timer-st {st_cls}">{st_txt}</div>', unsafe_allow_html=True)

            b1, b2, b3 = st.columns(3)
            with b1:
                lbl = "Pause" if ts["running"] else ("Resume" if el > 0 else "Start")
                if st.button(lbl, key=f"tbtn_{mid}", use_container_width=True, type="primary"):
                    if ts["running"]:
                        st.session_state.timers[mid]["seconds"] += int(time.time() - ts["start_ts"])
                        st.session_state.timers[mid].update({"running": False, "start_ts": None})
                    else:
                        st.session_state.timers[mid].update({"running": True, "start_ts": time.time()})
                    st.rerun()
            with b2:
                if st.button("Reset", key=f"trst_{mid}", use_container_width=True):
                    st.session_state.timers[mid] = {"running": False, "seconds": 0, "type": ts["type"], "start_ts": None}
                    st.rerun()
            with b3:
                ok = el >= 60
                if st.button("Save", key=f"tlog_{mid}", use_container_width=True, disabled=not ok):
                    ef = (ts["seconds"] + int(time.time() - ts["start_ts"]) if ts["running"] else ts["seconds"])
                    db.log_timer_session(mid, ts["type"], ef)
                    st.session_state.timers[mid] = {"running": False, "seconds": 0, "type": ts["type"], "start_ts": None}
                    st.success(f"Saved {fmt(ef)} for {m['name']}")
                    st.rerun()
                if not ok: st.caption("Min. 1 min to save")

            st.markdown("---")

        st.markdown('<div class="sh"><span class="sh-dot" style="background:#D97706"></span>Manual entry</div>', unsafe_allow_html=True)
        with st.form("manual_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                mm  = st.selectbox("Member", [m["name"] for m in members])
                md  = st.date_input("Date", value=date.today())
            with c2:
                ch2 = st.number_input("Work hours",  min_value=0.0, max_value=24.0, step=0.5)
                sh2 = st.number_input("Study hours", min_value=0.0, max_value=24.0, step=0.5)
            if st.form_submit_button("Save Entry", use_container_width=True):
                mid2 = members[[m["name"] for m in members].index(mm)]["id"]
                ds = md.isoformat(); saved = False
                if ch2 > 0: db.add_log(mid2, ds, "company",   ch2); saved = True
                if sh2 > 0: db.add_log(mid2, ds, "education", sh2); saved = True
                st.success("Entry saved.") if saved else st.warning("Enter at least one value.")

    with rc:
        st.markdown('<div class="sh"><span class="sh-dot" style="background:#0D9488"></span>Tasks</div>', unsafe_allow_html=True)
        mn   = [m["name"] for m in members]
        mi   = [m["id"]   for m in members]
        si   = mi.index(st.session_state.active_member_id) if st.session_state.active_member_id in mi else 0
        cho  = st.selectbox("Member", mn, index=si, label_visibility="collapsed")
        tmid = mi[mn.index(cho)]

        with st.form(key=f"tf_{tmid}", clear_on_submit=True):
            ta, tb, tc2 = st.columns([3, 1, 1])
            with ta: tn = st.text_input("Task", placeholder="Add a task…", label_visibility="collapsed")
            with tb: ttype = st.selectbox("Type", ["company","education"], label_visibility="collapsed",
                                          format_func=lambda x: "Work" if x=="company" else "Study")
            with tc2:
                if st.form_submit_button("Add", use_container_width=True) and tn.strip():
                    db.add_task(tmid, tn.strip(), ttype); st.rerun()

        mt = db.get_tasks(tmid)
        if not mt:
            st.markdown('<p style="color:var(--text-4);font-size:13px;padding:8px 0">No tasks yet.</p>', unsafe_allow_html=True)
        else:
            done_count = sum(1 for t in mt if t["done"])
            st.markdown(f"""
<div style="display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap">
  <span class="stat-pill sp-indigo">{len(mt)} total</span>
  <span class="stat-pill sp-teal">{done_count} done</span>
  <span class="stat-pill sp-amber">{len(mt)-done_count} remaining</span>
</div>""", unsafe_allow_html=True)

            for task in mt:
                bc  = "tb-w" if task["task_type"] == "company" else "tb-s"
                bl  = "work" if task["task_type"] == "company" else "study"
                ts2 = "text-decoration:line-through;color:var(--text-4)" if task["done"] else ""
                cc, ct, cd = st.columns([0.07, 0.75, 0.18])
                with cc:
                    chk = st.checkbox("", value=bool(task["done"]), key=f"chk_{task['id']}", label_visibility="collapsed")
                    if chk != bool(task["done"]): db.toggle_task(task["id"]); st.rerun()
                with ct:
                    st.markdown(f'<div style="font-size:13px;padding-top:6px;{ts2}">{task["name"]}&nbsp;<span class="tbadge {bc}">{bl}</span></div>', unsafe_allow_html=True)
                with cd:
                    if st.button("✕", key=f"del_{task['id']}", help="Remove"): db.delete_task(task["id"]); st.rerun()

    if any(t.get("running") for t in st.session_state.timers.values()):
        time.sleep(1); st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_gr:
    am = get_am()
    gn = [m["name"] for m in members]
    gi = [m["id"]   for m in members]
    gs = st.radio("Member", gn, index=gi.index(am["id"]) if am["id"] in gi else 0,
                  horizontal=True, label_visibility="collapsed")
    gm   = members[gn.index(gs)]
    days = [(date.today() - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
    dh   = db.get_daily_hours(gm["id"], days)

    CHART_COLORS = ["#4F46E5", "#0D9488", "#D97706", "#E11D48", "#7C3AED", "#2563EB"]

    BL = dict(
        margin=dict(l=0, r=0, t=28, b=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter,sans-serif", size=11),
        legend=dict(orientation="h", y=-0.28, font_size=11),
        xaxis=dict(showgrid=False, tickfont_size=11, linecolor="#E2E8F0"),
        yaxis=dict(gridcolor="rgba(0,0,0,.05)", tickfont_size=11, zerolinecolor="#E2E8F0"),
        hoverlabel=dict(bgcolor="#fff", bordercolor="#E2E8F0", font_size=12),
    )

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.caption(f"Daily hours — {gm['name']}")
        fig = go.Figure()
        fig.add_bar(x=[d[5:] for d in days], y=[dh[d]["company"]   for d in days],
                    name="Work",  marker_color="#4F46E5", marker_line_width=0,
                    marker_opacity=0.9)
        fig.add_bar(x=[d[5:] for d in days], y=[dh[d]["education"] for d in days],
                    name="Study", marker_color="#0D9488", marker_line_width=0,
                    marker_opacity=0.9)
        fig.update_layout(barmode="group", height=260, **BL)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.caption(f"All-time split — {gm['name']}")
        logs = db.get_logs(gm["id"])
        tc2  = round(sum(l["hours"] for l in logs if l["log_type"] == "company"),   2)
        ts2  = round(sum(l["hours"] for l in logs if l["log_type"] == "education"), 2)
        fig2 = go.Figure(go.Pie(
            labels=["Work", "Study"], values=[tc2 or 0, ts2 or 0],
            hole=0.65, marker_colors=["#4F46E5", "#0D9488"],
            textfont_size=12,
            marker=dict(line=dict(color="#fff", width=3)),
        ))
        fig2.update_layout(height=260, margin=dict(l=0,r=0,t=28,b=0),
                           legend=dict(orientation="h",y=-0.1,font_size=11),
                           paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter,sans-serif"))
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2, gap="medium")
    with c3:
        st.caption("Task completion — team")
        td = db.get_task_completion(members)
        cp = [round(td[m["id"]]["company"]["done"]  /td[m["id"]]["company"]["total"]*100)   if td[m["id"]]["company"]["total"]   else 0 for m in members]
        sp = [round(td[m["id"]]["education"]["done"]/td[m["id"]]["education"]["total"]*100) if td[m["id"]]["education"]["total"] else 0 for m in members]
        fig3 = go.Figure()
        fig3.add_bar(x=[m["name"] for m in members], y=cp, name="Work",  marker_color="#4F46E5", marker_opacity=0.9)
        fig3.add_bar(x=[m["name"] for m in members], y=sp, name="Study", marker_color="#0D9488", marker_opacity=0.9)
        fig3.update_layout(barmode="group", height=260,
                           **{**BL,
                              "yaxis": dict(range=[0,100], ticksuffix="%", gridcolor="rgba(0,0,0,.05)", tickfont_size=11, zerolinecolor="#E2E8F0"),
                              "xaxis": dict(showgrid=False, tickfont_size=11, linecolor="#E2E8F0")})
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.caption(f"Monthly trend — {gm['name']}")
        td2 = date.today(); ml = []
        d2  = td2.replace(day=1)
        for _ in range(6):
            ml.append((d2.year, d2.month))
            d2 = (d2 - timedelta(days=1)).replace(day=1)
        ml.reverse()
        mh  = db.get_monthly_hours(gm["id"], ml)
        lbl = [datetime(y,mo,1).strftime("%b") for y,mo in ml]
        fig4 = go.Figure()
        fig4.add_scatter(x=lbl, y=[mh[(y,mo)]["company"]   for y,mo in ml], name="Work",
                         line=dict(color="#4F46E5", width=2.5), fill="tozeroy",
                         fillcolor="rgba(79,70,229,.08)", mode="lines+markers",
                         marker=dict(size=7, color="#4F46E5", line=dict(color="#fff",width=2)))
        fig4.add_scatter(x=lbl, y=[mh[(y,mo)]["education"] for y,mo in ml], name="Study",
                         line=dict(color="#0D9488", width=2.5), fill="tozeroy",
                         fillcolor="rgba(13,148,136,.08)", mode="lines+markers",
                         marker=dict(size=7, color="#0D9488", line=dict(color="#fff",width=2)))
        fig4.update_layout(height=260, **BL)
        st.plotly_chart(fig4, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TEAM
# ═══════════════════════════════════════════════════════════════════════════════
with tab_tm:
    fl, fr = st.columns([2, 3], gap="large")
    with fl:
        st.markdown('<div class="sh"><span class="sh-dot" style="background:#7C3AED"></span>Add member</div>', unsafe_allow_html=True)
        with st.form("add_member_form", clear_on_submit=True):
            nn = st.text_input("Name", placeholder="Full name")
            nr = st.text_input("Role", placeholder="e.g. Developer")
            st.markdown('<div style="font-size:12px;font-weight:600;color:var(--text-2);margin-bottom:4px">Avatar colour</div>', unsafe_allow_html=True)
            sw = '<div class="swatches">'
            for i, col in enumerate(db.AVATAR_COLORS):
                sc = "sel" if i == st.session_state.selected_color else ""
                sw += f'<div class="swatch {sc}" style="background:{col["bg"]};border-color:{col["fg"] if sc else "transparent"}"></div>'
            st.markdown(sw + "</div>", unsafe_allow_html=True)
            cn = [f"Color {i+1}" for i in range(len(db.AVATAR_COLORS))]
            pc = st.radio("Colour", cn, index=st.session_state.selected_color, horizontal=True, label_visibility="collapsed")
            st.session_state.selected_color = cn.index(pc)
            if st.form_submit_button("Add Member", use_container_width=True) and nn.strip():
                db.add_member(nn.strip(), nr.strip() or "Team member", st.session_state.selected_color)
                st.success(f"Added {nn}."); st.rerun()

    with fr:
        st.markdown('<div class="sh"><span class="sh-dot" style="background:#4F46E5"></span>Current team</div>', unsafe_allow_html=True)
        ams  = db.get_members()
        cols = st.columns(min(3, len(ams)))
        for i, m in enumerate(ams):
            c2 = gc(m)
            with cols[i % len(cols)]:
                st.markdown(f"""
<div class="tmcard">
  <div class="tm-av" style="background:{c2['bg']};color:{c2['fg']}">{ini(m['name'])}</div>
  <div class="tm-nm">{m['name']}</div>
  <div class="tm-rl">{m['role']}</div>
</div>""", unsafe_allow_html=True)
                if st.button("Remove", key=f"rem_{m['id']}", use_container_width=True):
                    if len(ams) <= 1:
                        st.error("Need at least one member.")
                    else:
                        db.remove_member(m["id"])
                        if st.session_state.active_member_id == m["id"]:
                            rem = [x for x in ams if x["id"] != m["id"]]
                            if rem: st.session_state.active_member_id = rem[0]["id"]
                        st.rerun()
