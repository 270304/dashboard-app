"""
app.py — Team Productivity Dashboard (Streamlit)
Run: streamlit run app.py
"""
import time
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
import streamlit as st

import backend as db

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Team Productivity",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.init_db()

# ── global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* ── tokens ── */
:root {
  --blue:       #2563EB;
  --blue-50:    #EFF6FF;
  --blue-100:   #DBEAFE;
  --blue-700:   #1D4ED8;
  --green:      #16A34A;
  --green-50:   #F0FDF4;
  --green-100:  #DCFCE7;
  --green-700:  #15803D;
  --surface:    #F9FAFB;
  --surface-2:  #F3F4F6;
  --border:     #E5E7EB;
  --border-d:   #D1D5DB;
  --text-1:     #111827;
  --text-2:     #374151;
  --text-3:     #6B7280;
  --text-4:     #9CA3AF;
  --r-s: 6px; --r-m: 10px; --r-l: 14px; --r-xl: 18px;
}

/* hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 100% !important; }

/* ── sidebar ── */
[data-testid="stSidebar"] { background: #fff; border-right: 1px solid var(--border); }
[data-testid="stSidebar"] > div { padding: 1.5rem 1.25rem; }

.sb-brand {
  display: flex; align-items: center; gap: 10px;
  padding-bottom: 1.25rem; border-bottom: 1px solid var(--border); margin-bottom: 1.25rem;
}
.sb-icon {
  width: 34px; height: 34px; border-radius: 9px; background: var(--blue);
  display: flex; align-items: center; justify-content: center; font-size: 15px; flex-shrink: 0;
}
.sb-title { font-size: 14px; font-weight: 600; color: var(--text-1); }
.sb-sub   { font-size: 11px; color: var(--text-3); }

.sb-section {
  font-size: 10px; font-weight: 600; letter-spacing: .7px;
  text-transform: uppercase; color: var(--text-4); margin: 1.25rem 0 .6rem;
}

.smcard {
  display: flex; align-items: center; gap: 10px; padding: 8px 10px;
  border-radius: var(--r-m); border: 1px solid transparent; margin-bottom: 3px; background: #fff;
}
.smcard.active { background: var(--blue-50); border-color: var(--blue-100); }
.savatar {
  width: 34px; height: 34px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600;
}
.sname { font-size: 13px; font-weight: 500; color: var(--text-1); }
.srole { font-size: 11px; color: var(--text-3); }
.sbadge {
  margin-left: auto; font-size: 11px; font-weight: 600; padding: 2px 8px;
  border-radius: 20px; white-space: nowrap; background: var(--surface-2); color: var(--text-3);
}
.smcard.active .sbadge { background: var(--blue-100); color: var(--blue-700); }

/* ── page header ── */
.pg-header {
  display: flex; align-items: flex-end; justify-content: space-between;
  margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border);
}
.pg-title { font-size: 20px; font-weight: 600; color: var(--text-1); }
.pg-sub   { font-size: 13px; color: var(--text-3); margin-top: 2px; }

/* ── metric grid ── */
.mg { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-bottom: 1.75rem; }
.mc2 {
  background: #fff; border: 1px solid var(--border);
  border-radius: var(--r-l); padding: 1.1rem 1.25rem;
  position: relative; overflow: hidden;
}
.mc2 .lbl { font-size: 12px; color: var(--text-3); font-weight: 500; margin-bottom: 6px; }
.mc2 .val { font-size: 28px; font-weight: 600; color: var(--text-1); letter-spacing: -.5px; line-height: 1; }
.mc2 .sub { font-size: 11px; color: var(--text-4); margin-top: 5px; }
.mc2 .bar { position: absolute; right:0; top:0; bottom:0; width:4px; border-radius: 0 var(--r-l) var(--r-l) 0; }

/* ── section heading ── */
.sh {
  font-size: 13px; font-weight: 600; color: var(--text-1);
  margin: 1.5rem 0 .75rem; display: flex; align-items: center; gap: 8px;
}
.sh::after { content:''; flex:1; height:1px; background: var(--border); }

/* ── bar rows ── */
.br { display:flex; align-items:center; gap:12px; margin-bottom:8px; }
.bn { font-size:13px; color:var(--text-2); width:80px; flex-shrink:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.bn.bold { font-weight:600; color:var(--text-1); }
.bs { flex:1; display:flex; flex-direction:column; gap:3px; }
.bt { height:6px; background:var(--surface-2); border-radius:3px; overflow:hidden; }
.bf { height:100%; border-radius:3px; }
.bv { font-size:12px; color:var(--text-2); font-weight:500; width:38px; text-align:right; }

.legend { display:flex; gap:16px; font-size:12px; color:var(--text-3); margin-top:10px; }
.ldot   { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:5px; }

/* ── timer card ── */
.tc {
  background:#fff; border:1px solid var(--border); border-radius:var(--r-xl);
  padding:1.25rem 1.5rem; margin-bottom:1rem;
}
.tc-hdr { display:flex; align-items:center; gap:10px; margin-bottom:.75rem; }
.tc-av  {
  width:38px; height:38px; border-radius:50%; flex-shrink:0;
  display:flex; align-items:center; justify-content:center; font-size:13px; font-weight:600;
}
.tc-nm { font-size:14px; font-weight:600; color:var(--text-1); }
.tc-rl { font-size:12px; color:var(--text-3); }
.running-dot {
  width:8px; height:8px; border-radius:50%; background:#16A34A; margin-left:auto;
  animation: pulse 1.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(.8)} }
.timer-digits {
  font-family:'JetBrains Mono',monospace; font-size:44px; font-weight:500;
  text-align:center; letter-spacing:2px; padding:8px 0; line-height:1;
}
.timer-st { text-align:center; font-size:12px; color:var(--text-4); height:18px; margin-bottom:10px; }

/* ── task rows ── */
.trow {
  display:flex; align-items:center; gap:8px; padding:8px 12px;
  background:#fff; border:1px solid var(--border); border-radius:var(--r-m); margin-bottom:4px;
}
.trow:hover { border-color:var(--border-d); }
.ttxt { font-size:13px; color:var(--text-1); flex:1; }
.ttxt.done { text-decoration:line-through; color:var(--text-4); }
.tbadge { font-size:10px; font-weight:600; padding:2px 8px; border-radius:20px; }
.tb-w { background:var(--blue-50);  color:var(--blue-700); }
.tb-s { background:var(--green-50); color:var(--green-700); }

/* ── team cards ── */
.tmcard {
  background:#fff; border:1px solid var(--border); border-radius:var(--r-l);
  padding:1.25rem 1rem; text-align:center; margin-bottom:10px;
}
.tm-av {
  width:54px; height:54px; border-radius:50%; margin:0 auto 10px;
  display:flex; align-items:center; justify-content:center; font-size:17px; font-weight:600;
}
.tm-nm { font-size:14px; font-weight:600; color:var(--text-1); }
.tm-rl { font-size:12px; color:var(--text-3); margin-top:2px; }

/* ── swatches ── */
.swatches { display:flex; gap:6px; flex-wrap:wrap; margin:6px 0 12px; }
.swatch { width:24px; height:24px; border-radius:50%; cursor:pointer; border:2px solid transparent; transition:transform .1s; }
.swatch.sel { transform:scale(1.35); border-color:#374151; }

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

def av(m, sz=40, cls="avatar"):
    c = gc(m); fs = max(11, sz // 3)
    return f'<div class="{cls}" style="width:{sz}px;height:{sz}px;background:{c["bg"]};color:{c["fg"]};font-size:{fs}px">{ini(m["name"])}</div>'

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
        tot  = round(db.sum_hours(m["id"], "company", vl()) + db.sum_hours(m["id"], "education", vl()), 1)
        act  = "active" if m["id"] == st.session_state.active_member_id else ""
        c    = gc(m)
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
am = get_am()
today_str = date.today().strftime("%A, %d %B %Y")
vs = "Today" if vl() == "today" else "This Month"

st.markdown(f"""
<div class="pg-header">
  <div>
    <div class="pg-title">Good day, {am['name'].split()[0]} 👋</div>
    <div class="pg-sub">{today_str} &nbsp;·&nbsp; {vs}</div>
  </div>
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
  <div class="mc2">
    <div class="lbl">Total Hours</div>
    <div class="val">{th}</div>
    <div class="sub">of {tgt}h target</div>
    <div class="bar" style="background:#6366F1"></div>
  </div>
  <div class="mc2">
    <div class="lbl">Work Hours</div>
    <div class="val">{ch}</div>
    <div class="sub">company time</div>
    <div class="bar" style="background:#2563EB"></div>
  </div>
  <div class="mc2">
    <div class="lbl">Study Hours</div>
    <div class="val">{sh}</div>
    <div class="sub">learning &amp; education</div>
    <div class="bar" style="background:#16A34A"></div>
  </div>
  <div class="mc2">
    <div class="lbl">Tasks Done</div>
    <div class="val">{dt}<span style="font-size:16px;color:var(--text-4);font-weight:400">/{tt}</span></div>
    <div class="sub">{tpct}% completion rate</div>
    <div class="bar" style="background:#D97706"></div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="sh">Team hours breakdown</div>', unsafe_allow_html=True)
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
    <div class="bt"><div class="bf" style="width:{cpct}%;background:#2563EB"></div></div>
    <div class="bt"><div class="bf" style="width:{spct}%;background:#16A34A"></div></div>
  </div>
  <div class="bv">{tot}h</div>
</div>""", unsafe_allow_html=True)
    st.markdown("""<div class="legend">
  <span><span class="ldot" style="background:#2563EB"></span>Work</span>
  <span><span class="ldot" style="background:#16A34A"></span>Study</span>
</div>""", unsafe_allow_html=True)

    st.markdown(f'<div class="sh">Tasks — {am["name"]}</div>', unsafe_allow_html=True)
    if not tsks:
        st.caption("No tasks yet. Add some in the Time Tracker tab.")
    else:
        for task in tsks:
            dc  = "done" if task["done"] else ""
            bc  = "tb-w" if task["task_type"] == "company" else "tb-s"
            bl  = "work" if task["task_type"] == "company" else "study"
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
        st.markdown('<div class="sh">Timers</div>', unsafe_allow_html=True)
        for m in members:
            mid = m["id"]
            if mid not in st.session_state.timers:
                st.session_state.timers[mid] = {"running": False, "seconds": 0, "type": "company", "start_ts": None}
            ts  = st.session_state.timers[mid]
            el  = elapsed(mid)
            cm  = gc(m)
            iw  = ts["type"] == "company"
            tc  = "#2563EB" if iw else "#16A34A"
            rdot = '<div class="running-dot"></div>' if ts["running"] else ""

            st.markdown(f"""
<div class="tc">
  <div class="tc-hdr">
    <div class="tc-av" style="background:{cm['bg']};color:{cm['fg']}">{ini(m['name'])}</div>
    <div><div class="tc-nm">{m['name']}</div><div class="tc-rl">{m['role']}</div></div>
    {rdot}
  </div>
</div>""", unsafe_allow_html=True)

            tt1, tt2 = st.columns(2)
            with tt1:
                if st.button("Work",  key=f"tw_{mid}", use_container_width=True,
                             type="primary" if iw else "secondary", disabled=ts["running"]):
                    st.session_state.timers[mid]["type"] = "company"; st.rerun()
            with tt2:
                if st.button("Study", key=f"ts_{mid}", use_container_width=True,
                             type="primary" if not iw else "secondary", disabled=ts["running"]):
                    st.session_state.timers[mid]["type"] = "education"; st.rerun()

            st.markdown(f'<div class="timer-digits" style="color:{tc}">{fmt(el)}</div>', unsafe_allow_html=True)
            if ts["running"]:   st_txt = "● Running"
            elif el > 0:        st_txt = f"Paused at {fmt(el)}"
            else:               st_txt = ""
            st.markdown(f'<div class="timer-st">{st_txt}</div>', unsafe_allow_html=True)

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

        st.markdown('<div class="sh">Manual entry</div>', unsafe_allow_html=True)
        with st.form("manual_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                mm = st.selectbox("Member", [m["name"] for m in members])
                md = st.date_input("Date", value=date.today())
            with c2:
                ch2 = st.number_input("Work hours",  min_value=0.0, max_value=24.0, step=0.5)
                sh2 = st.number_input("Study hours", min_value=0.0, max_value=24.0, step=0.5)
            if st.form_submit_button("Save Entry", use_container_width=True):
                mid2 = members[[m["name"] for m in members].index(mm)]["id"]
                ds   = md.isoformat(); saved = False
                if ch2 > 0: db.add_log(mid2, ds, "company",   ch2); saved = True
                if sh2 > 0: db.add_log(mid2, ds, "education", sh2); saved = True
                st.success("Entry saved.") if saved else st.warning("Enter at least one value.")

    with rc:
        st.markdown('<div class="sh">Tasks</div>', unsafe_allow_html=True)
        mn    = [m["name"] for m in members]
        mi    = [m["id"]   for m in members]
        si    = mi.index(st.session_state.active_member_id) if st.session_state.active_member_id in mi else 0
        cho   = st.selectbox("Member", mn, index=si, label_visibility="collapsed")
        tmid  = mi[mn.index(cho)]

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
            st.caption("No tasks yet.")
        else:
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

    BL = dict(
        margin=dict(l=0,r=0,t=24,b=0), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter,sans-serif", size=11),
        legend=dict(orientation="h", y=-0.25, font_size=11),
        xaxis=dict(showgrid=False, tickfont_size=11, linecolor="#E5E7EB"),
        yaxis=dict(gridcolor="rgba(0,0,0,.05)", tickfont_size=11),
        hoverlabel=dict(bgcolor="#fff", bordercolor="#E5E7EB", font_size=12),
    )

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.caption(f"Daily hours — {gm['name']}")
        fig = go.Figure()
        fig.add_bar(x=[d[5:] for d in days], y=[dh[d]["company"]   for d in days], name="Work",  marker_color="#2563EB", marker_line_width=0)
        fig.add_bar(x=[d[5:] for d in days], y=[dh[d]["education"] for d in days], name="Study", marker_color="#16A34A", marker_line_width=0)
        fig.update_layout(barmode="group", height=260, **BL)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.caption(f"All-time split — {gm['name']}")
        logs = db.get_logs(gm["id"])
        tc2  = round(sum(l["hours"] for l in logs if l["log_type"] == "company"),   2)
        ts2  = round(sum(l["hours"] for l in logs if l["log_type"] == "education"), 2)
        fig2 = go.Figure(go.Pie(labels=["Work","Study"], values=[tc2 or 0, ts2 or 0],
                                hole=0.65, marker_colors=["#2563EB","#16A34A"], textfont_size=12))
        fig2.update_layout(height=260, margin=dict(l=0,r=0,t=24,b=0),
                           legend=dict(orientation="h",y=-0.1,font_size=11),
                           paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter,sans-serif"))
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2, gap="medium")
    with c3:
        st.caption("Task completion — team")
        td   = db.get_task_completion(members)
        cp   = [round(td[m["id"]]["company"]["done"]  /td[m["id"]]["company"]["total"]*100)   if td[m["id"]]["company"]["total"]   else 0 for m in members]
        sp   = [round(td[m["id"]]["education"]["done"]/td[m["id"]]["education"]["total"]*100) if td[m["id"]]["education"]["total"] else 0 for m in members]
        fig3 = go.Figure()
        fig3.add_bar(x=[m["name"] for m in members], y=cp, name="Work",  marker_color="#2563EB")
        fig3.add_bar(x=[m["name"] for m in members], y=sp, name="Study", marker_color="#16A34A")
        fig3.update_layout(barmode="group", height=260,
                           **{**BL, "yaxis": dict(range=[0,100], ticksuffix="%", gridcolor="rgba(0,0,0,.05)", tickfont_size=11),
                                    "xaxis": dict(showgrid=False, tickfont_size=11)})
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
                         line_color="#2563EB", fill="tozeroy", fillcolor="rgba(37,99,235,.06)",
                         mode="lines+markers", marker=dict(size=5))
        fig4.add_scatter(x=lbl, y=[mh[(y,mo)]["education"] for y,mo in ml], name="Study",
                         line_color="#16A34A", fill="tozeroy", fillcolor="rgba(22,163,74,.06)",
                         mode="lines+markers", marker=dict(size=5))
        fig4.update_layout(height=260, **BL)
        st.plotly_chart(fig4, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TEAM
# ═══════════════════════════════════════════════════════════════════════════════
with tab_tm:
    fl, fr = st.columns([2, 3], gap="large")
    with fl:
        st.markdown('<div class="sh">Add member</div>', unsafe_allow_html=True)
        with st.form("add_member_form", clear_on_submit=True):
            nn = st.text_input("Name", placeholder="Full name")
            nr = st.text_input("Role", placeholder="e.g. Developer")
            st.markdown("Avatar colour")
            sw = '<div class="swatches">'
            for i, col in enumerate(db.AVATAR_COLORS):
                sc = "sel" if i == st.session_state.selected_color else ""
                sw += f'<div class="swatch {sc}" style="background:{col["bg"]};border-color:{col["fg"] if sc else "transparent"}"></div>'
            st.markdown(sw + "</div>", unsafe_allow_html=True)
            cn  = [f"Color {i+1}" for i in range(len(db.AVATAR_COLORS))]
            pc  = st.radio("Colour", cn, index=st.session_state.selected_color, horizontal=True, label_visibility="collapsed")
            st.session_state.selected_color = cn.index(pc)
            if st.form_submit_button("Add Member", use_container_width=True) and nn.strip():
                db.add_member(nn.strip(), nr.strip() or "Team member", st.session_state.selected_color)
                st.success(f"Added {nn}."); st.rerun()

    with fr:
        st.markdown('<div class="sh">Current team</div>', unsafe_allow_html=True)
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
