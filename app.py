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
    page_title="Team Productivity Dashboard",
    page_icon="📊",
    layout="centered",
)

# ── init DB ───────────────────────────────────────────────────────────────────
db.init_db()

# ── global CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif !important;
}

/* ── brand tokens ── */
:root {
  --blue:       #185FA5;
  --blue-light: #E6F1FB;
  --blue-dark:  #0C447C;
  --green:      #3B6D11;
  --green-light:#EAF3DE;
  --green-dark: #27500A;
  --surface:    #F8F8F7;
  --border:     rgba(0,0,0,0.08);
  --text-main:  #1a1a1a;
  --text-muted: #6b7280;
  --text-hint:  #9ca3af;
  --radius-sm:  8px;
  --radius-md:  12px;
  --radius-lg:  16px;
}

/* ── header ── */
.dash-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}
.dash-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-main);
  letter-spacing: -0.3px;
}

/* ── member cards ── */
.member-cards { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 1.25rem; }
.mcard {
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 14px 12px;
  text-align: center;
  min-width: 130px;
  flex: 1 1 130px;
  background: #fff;
  transition: border-color .15s, box-shadow .15s;
  cursor: pointer;
}
.mcard:hover { border-color: var(--blue); }
.mcard.active { border: 1.5px solid var(--blue); background: var(--blue-light); }
.mcard .avatar {
  width: 44px; height: 44px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 600; font-size: 14px; margin: 0 auto 8px;
}
.mcard .mname  { font-size: 13px; font-weight: 600; color: var(--text-main); }
.mcard .mrole  { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
.mcard .mstats {
  display: flex; gap: 6px; justify-content: center;
  margin-top: 8px; flex-wrap: wrap;
  font-size: 11px; color: var(--text-hint);
}
.mcard .mstats span { font-weight: 600; color: var(--text-main); }

/* ── bars ── */
.bar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.bar-wrap { flex: 1; }
.bar-track { height: 6px; background: #EFEFED; border-radius: 4px; overflow: hidden; margin-bottom: 3px; }
.bar-fill  { height: 100%; border-radius: 4px; }

/* ── task items ── */
.task-item {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 10px; border: 1px solid var(--border);
  border-radius: var(--radius-sm); font-size: 13px; margin-bottom: 4px;
  background: #fff;
}
.task-item.done { opacity: .4; text-decoration: line-through; }
.badge {
  font-size: 11px; padding: 2px 8px; border-radius: 20px;
  font-weight: 500; margin-left: auto; white-space: nowrap;
}
.badge-company   { background: var(--blue-light);  color: var(--blue-dark);  }
.badge-education { background: var(--green-light); color: var(--green-dark); }

/* ── timer ── */
.timer-display {
  font-size: 48px; font-weight: 600; text-align: center;
  font-variant-numeric: tabular-nums; letter-spacing: 1px;
  padding: 12px 0; line-height: 1;
}
.timer-status {
  text-align: center; font-size: 12px;
  color: var(--text-muted); margin-bottom: 4px;
}

/* ── colour swatches ── */
.swatches { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 6px; }
.swatch {
  width: 26px; height: 26px; border-radius: 50%; cursor: pointer;
  border: 2px solid transparent; display: inline-block; transition: transform .1s;
}
.swatch.sel { transform: scale(1.3); border-color: #555; }

/* ── section header ── */
.section-label {
  font-size: 11px; font-weight: 600; letter-spacing: .6px;
  text-transform: uppercase; color: var(--text-muted);
  margin-bottom: 10px; margin-top: 4px;
}

/* ── legend dots ── */
.legend { display: flex; gap: 14px; font-size: 12px; color: var(--text-muted); margin-top: 8px; }
.legend-dot {
  display: inline-block; width: 8px; height: 8px;
  border-radius: 50%; margin-right: 5px; vertical-align: middle;
}

@media(max-width:600px){
  .timer-display { font-size: 36px; }
}
</style>
""",
    unsafe_allow_html=True,
)

# ── session state ─────────────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "active_member_id": None,
        "view": "today",
        "tab": "overview",
        "timers": {},
        "selected_color": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ── helpers ───────────────────────────────────────────────────────────────────
def get_members_cached():
    return db.get_members()

members = get_members_cached()
if not members:
    st.error("No members found – check your database configuration.")
    st.stop()

if st.session_state.active_member_id not in [m["id"] for m in members]:
    st.session_state.active_member_id = members[0]["id"]

def initials(name: str) -> str:
    return "".join(w[0] for w in name.split())[:2].upper()

def avatar_html(m: dict, size: int = 44) -> str:
    c = db.AVATAR_COLORS[m["color_idx"] % len(db.AVATAR_COLORS)]
    ini = initials(m["name"])
    return (
        f'<div class="avatar" style="width:{size}px;height:{size}px;'
        f'background:{c["bg"]};color:{c["fg"]};font-size:{max(11, size//3)}px">{ini}</div>'
    )

def fmt_hms(secs: int) -> str:
    h, rem = divmod(secs, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def timer_elapsed(mid: int) -> int:
    t = st.session_state.timers.get(mid, {})
    base = t.get("seconds", 0)
    if t.get("running") and t.get("start_ts"):
        base += int(time.time() - t["start_ts"])
    return base

def get_active_member():
    mid = st.session_state.active_member_id
    return next((m for m in members if m["id"] == mid), members[0])

# ── TOP BAR ───────────────────────────────────────────────────────────────────
col_title, col_views = st.columns([3, 2])
with col_title:
    st.markdown('<div class="dash-title">Team Productivity</div>', unsafe_allow_html=True)
with col_views:
    view_choice = st.radio(
        "View",
        ["Today", "This Month"],
        index=0 if st.session_state.view == "today" else 1,
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state.view = "today" if view_choice == "Today" else "month"

st.markdown("---")

# ── NAV TABS ──────────────────────────────────────────────────────────────────
tabs = st.tabs(["Overview", "Track", "Graphs", "Team"])
tab_overview, tab_track, tab_graphs, tab_team = tabs

# ═══════════════════════════════════════════════════════════════════════════════
# TAB: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tab_overview:
    st.markdown('<div class="section-label">Select member</div>', unsafe_allow_html=True)
    m_names = [m["name"] for m in members]
    m_ids   = [m["id"]   for m in members]
    sel_idx = m_ids.index(st.session_state.active_member_id) if st.session_state.active_member_id in m_ids else 0
    chosen = st.radio(
        "Member", m_names,
        index=sel_idx,
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state.active_member_id = m_ids[m_names.index(chosen)]

    am   = get_active_member()
    view = st.session_state.view

    ch    = db.sum_hours(am["id"], "company", view)
    sh    = db.sum_hours(am["id"], "education", view)
    th    = round(ch + sh, 2)
    tasks = db.get_tasks(am["id"])
    dt    = sum(1 for t in tasks if t["done"])
    tt    = len(tasks)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Hours",   f"{th}h")
    c2.metric("Work Hours",    f"{ch}h")
    c3.metric("Study Hours",   f"{sh}h")
    c4.metric("Tasks Done",    f"{dt}/{tt}")

    st.markdown('<div class="section-label" style="margin-top:1.25rem">Hours breakdown</div>', unsafe_allow_html=True)
    target = 8 if view == "today" else 160
    st.caption(f"Target: {target}h / {'day' if view == 'today' else 'month'}")

    for m in members:
        mc   = db.sum_hours(m["id"], "company", view)
        ms   = db.sum_hours(m["id"], "education", view)
        tot  = round(mc + ms, 2)
        cpct = min(100, round(mc / target * 100))
        spct = min(100, round(ms / target * 100))
        bold = "font-weight:600;color:#1a1a1a" if m["id"] == am["id"] else ""
        st.markdown(
            f"""
<div class="bar-row">
  <div style="font-size:13px;color:#6b7280;width:76px;flex-shrink:0;{bold}">{m['name']}</div>
  <div class="bar-wrap">
    <div class="bar-track"><div class="bar-fill" style="width:{cpct}%;background:#185FA5"></div></div>
    <div class="bar-track"><div class="bar-fill" style="width:{spct}%;background:#3B6D11"></div></div>
  </div>
  <div style="font-size:13px;width:38px;text-align:right;color:#1a1a1a;font-weight:500">{tot}h</div>
</div>""",
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="legend">'
        '<span><span class="legend-dot" style="background:#185FA5"></span>Work</span>'
        '<span><span class="legend-dot" style="background:#3B6D11"></span>Study</span>'
        '</div>',
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB: TRACK
# ═══════════════════════════════════════════════════════════════════════════════
with tab_track:
    st.markdown('<div class="section-label">Timers</div>', unsafe_allow_html=True)

    for m in members:
        mid = m["id"]

        with st.expander(
            f"{m['name']} — {m['role']}", expanded=(mid == st.session_state.active_member_id)
        ):
            if mid not in st.session_state.timers:
                st.session_state.timers[mid] = {
                    "running": False,
                    "seconds": 0,
                    "type": "company",
                    "start_ts": None,
                }

            t_state = st.session_state.timers[mid]
            elapsed = timer_elapsed(mid)

            # timer type selector
            t_type_col1, t_type_col2 = st.columns(2)
            with t_type_col1:
                if st.button(
                    "Work",
                    key=f"ttype_company_{mid}",
                    type="primary" if t_state["type"] == "company" else "secondary",
                    disabled=t_state["running"],
                    use_container_width=True,
                ):
                    st.session_state.timers[mid]["type"] = "company"
                    st.rerun()
            with t_type_col2:
                if st.button(
                    "Study",
                    key=f"ttype_edu_{mid}",
                    type="primary" if t_state["type"] == "education" else "secondary",
                    disabled=t_state["running"],
                    use_container_width=True,
                ):
                    st.session_state.timers[mid]["type"] = "education"
                    st.rerun()

            # timer display
            timer_color = "#185FA5" if t_state["type"] == "company" else "#3B6D11"
            st.markdown(
                f'<div class="timer-display" style="color:{timer_color}">{fmt_hms(elapsed)}</div>',
                unsafe_allow_html=True,
            )

            if t_state["running"]:
                st.markdown('<div class="timer-status">Running</div>', unsafe_allow_html=True)
            elif elapsed > 0:
                st.markdown(f'<div class="timer-status">Paused at {fmt_hms(elapsed)}</div>', unsafe_allow_html=True)

            # controls
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            with btn_col1:
                start_label = "Pause" if t_state["running"] else ("Resume" if elapsed > 0 else "Start")
                if st.button(start_label, key=f"start_{mid}", use_container_width=True):
                    if t_state["running"]:
                        acc = int(time.time() - t_state["start_ts"])
                        st.session_state.timers[mid]["seconds"] += acc
                        st.session_state.timers[mid]["running"] = False
                        st.session_state.timers[mid]["start_ts"] = None
                    else:
                        st.session_state.timers[mid]["running"] = True
                        st.session_state.timers[mid]["start_ts"] = time.time()
                    st.rerun()

            with btn_col2:
                if st.button("Reset", key=f"reset_{mid}", use_container_width=True):
                    st.session_state.timers[mid] = {
                        "running": False, "seconds": 0,
                        "type": t_state["type"], "start_ts": None,
                    }
                    st.rerun()

            with btn_col3:
                log_disabled = elapsed < 60
                if st.button("Save", key=f"log_{mid}", use_container_width=True, disabled=log_disabled):
                    if t_state["running"]:
                        acc = int(time.time() - t_state["start_ts"])
                        elapsed_final = t_state["seconds"] + acc
                    else:
                        elapsed_final = t_state["seconds"]
                    db.log_timer_session(mid, t_state["type"], elapsed_final)
                    st.session_state.timers[mid] = {
                        "running": False, "seconds": 0,
                        "type": t_state["type"], "start_ts": None,
                    }
                    st.success(f"Saved {fmt_hms(elapsed_final)} for {m['name']}")
                    st.rerun()
                if log_disabled:
                    st.caption("Run at least 1 minute to save")

            # tasks
            st.markdown("---")
            st.markdown(f'<div class="section-label">Tasks — {m["name"]}</div>', unsafe_allow_html=True)

            with st.form(key=f"task_form_{mid}", clear_on_submit=True):
                tc1, tc2, tc3 = st.columns([3, 1, 1])
                with tc1:
                    task_name = st.text_input(
                        "Task", placeholder="Describe the task…", label_visibility="collapsed"
                    )
                with tc2:
                    task_type = st.selectbox(
                        "Type", ["company", "education"], label_visibility="collapsed"
                    )
                with tc3:
                    add_task_btn = st.form_submit_button("Add", use_container_width=True)
                if add_task_btn and task_name.strip():
                    db.add_task(mid, task_name.strip(), task_type)
                    st.rerun()

            member_tasks = db.get_tasks(mid)
            if not member_tasks:
                st.caption("No tasks yet.")
            else:
                for task in member_tasks:
                    badge_cls = "badge-company" if task["task_type"] == "company" else "badge-education"
                    badge_lbl = "work" if task["task_type"] == "company" else "study"
                    col_chk, col_txt, col_del = st.columns([0.07, 0.73, 0.20])
                    with col_chk:
                        chk = st.checkbox(
                            "", value=bool(task["done"]),
                            key=f"chk_{task['id']}", label_visibility="collapsed"
                        )
                        if chk != bool(task["done"]):
                            db.toggle_task(task["id"])
                            st.rerun()
                    with col_txt:
                        style = "text-decoration:line-through;opacity:.4" if task["done"] else ""
                        st.markdown(
                            f'<div style="font-size:13px;padding-top:5px;{style}">'
                            f'{task["name"]}&nbsp;<span class="badge {badge_cls}">{badge_lbl}</span></div>',
                            unsafe_allow_html=True,
                        )
                    with col_del:
                        if st.button("Remove", key=f"del_{task['id']}", help="Delete task"):
                            db.delete_task(task["id"])
                            st.rerun()

    # manual entry
    st.markdown("---")
    st.markdown('<div class="section-label">Manual entry</div>', unsafe_allow_html=True)
    with st.form("manual_form", clear_on_submit=True):
        mc1, mc2 = st.columns(2)
        with mc1:
            manual_member = st.selectbox("Member", [m["name"] for m in members], key="man_mem")
            manual_date   = st.date_input("Date", value=date.today(), key="man_date")
        with mc2:
            company_h = st.number_input("Work hours",  min_value=0.0, max_value=24.0, step=0.5, key="man_ch")
            study_h   = st.number_input("Study hours", min_value=0.0, max_value=24.0, step=0.5, key="man_sh")
        save_btn = st.form_submit_button("Save Entry", use_container_width=True)
        if save_btn:
            mid_man  = members[[m["name"] for m in members].index(manual_member)]["id"]
            date_str = manual_date.isoformat()
            if company_h > 0:
                db.add_log(mid_man, date_str, "company", company_h)
            if study_h > 0:
                db.add_log(mid_man, date_str, "education", study_h)
            if company_h > 0 or study_h > 0:
                st.success("Entry saved.")
            else:
                st.warning("Enter at least one value.")

    # auto-rerun while any timer is running
    if any(t.get("running") for t in st.session_state.timers.values()):
        time.sleep(1)
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB: GRAPHS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_graphs:
    am = get_active_member()

    st.markdown('<div class="section-label">Viewing graphs for</div>', unsafe_allow_html=True)
    g_names = [m["name"] for m in members]
    g_ids   = [m["id"]   for m in members]
    g_sel   = st.radio(
        "Graph member", g_names,
        index=g_ids.index(am["id"]) if am["id"] in g_ids else 0,
        horizontal=True,
        label_visibility="collapsed",
    )
    gm = members[g_names.index(g_sel)]

    days   = [(date.today() - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
    daily  = db.get_daily_hours(gm["id"], days)

    CHART_LAYOUT = dict(
        height=230,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", y=-0.28, font_size=12),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, tickfont_size=11),
        yaxis=dict(gridcolor="rgba(0,0,0,.05)", tickfont_size=11),
        font=dict(family="DM Sans, sans-serif"),
    )

    col_bar, col_donut = st.columns(2)

    with col_bar:
        st.caption(f"Daily hours — {gm['name']}")
        fig_bar = go.Figure()
        fig_bar.add_bar(
            x=[d[5:] for d in days],
            y=[daily[d]["company"] for d in days],
            name="Work", marker_color="#185FA5", marker_line_width=0,
        )
        fig_bar.add_bar(
            x=[d[5:] for d in days],
            y=[daily[d]["education"] for d in days],
            name="Study", marker_color="#3B6D11", marker_line_width=0,
        )
        fig_bar.update_layout(barmode="group", **CHART_LAYOUT)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_donut:
        st.caption("All-time split")
        all_logs = db.get_logs(gm["id"])
        total_c  = round(sum(l["hours"] for l in all_logs if l["log_type"] == "company"), 2)
        total_s  = round(sum(l["hours"] for l in all_logs if l["log_type"] == "education"), 2)
        fig_donut = go.Figure(
            go.Pie(
                labels=["Work", "Study"],
                values=[total_c or 0, total_s or 0],
                hole=0.64,
                marker_colors=["#185FA5", "#3B6D11"],
                textfont_size=12,
            )
        )
        fig_donut.update_layout(
            height=230,
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h", y=-0.1, font_size=12),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans, sans-serif"),
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    col_task_chart, col_trend = st.columns(2)

    with col_task_chart:
        st.caption("Task completion rate")
        tc_data   = db.get_task_completion(members)
        comp_pct  = []
        study_pct = []
        for m in members:
            s  = tc_data[m["id"]]
            cp = round(s["company"]["done"]   / s["company"]["total"]   * 100) if s["company"]["total"]   else 0
            sp = round(s["education"]["done"] / s["education"]["total"] * 100) if s["education"]["total"] else 0
            comp_pct.append(cp)
            study_pct.append(sp)
        fig_tc = go.Figure()
        fig_tc.add_bar(x=[m["name"] for m in members], y=comp_pct,  name="Work",  marker_color="#185FA5")
        fig_tc.add_bar(x=[m["name"] for m in members], y=study_pct, name="Study", marker_color="#3B6D11")
        fig_tc.update_layout(
            barmode="group",
            yaxis=dict(range=[0, 100], ticksuffix="%", gridcolor="rgba(0,0,0,.05)", tickfont_size=11),
            xaxis=dict(showgrid=False, tickfont_size=11),
            **{k: v for k, v in CHART_LAYOUT.items() if k not in ("yaxis", "xaxis")},
        )
        st.plotly_chart(fig_tc, use_container_width=True)

    with col_trend:
        st.caption(f"Monthly trend — {gm['name']}")
        today_d    = date.today()
        month_list = []
        d = today_d.replace(day=1)
        for _ in range(6):
            month_list.append((d.year, d.month))
            d = (d - timedelta(days=1)).replace(day=1)
        month_list.reverse()
        monthly   = db.get_monthly_hours(gm["id"], month_list)
        mo_labels = [f"{datetime(y, m, 1).strftime('%b')}" for y, m in month_list]
        fig_trend = go.Figure()
        fig_trend.add_scatter(
            x=mo_labels,
            y=[monthly[(y, m)]["company"] for y, m in month_list],
            name="Work", line_color="#185FA5",
            fill="tozeroy", fillcolor="rgba(24,95,165,.07)",
            mode="lines+markers",
        )
        fig_trend.add_scatter(
            x=mo_labels,
            y=[monthly[(y, m)]["education"] for y, m in month_list],
            name="Study", line_color="#3B6D11",
            fill="tozeroy", fillcolor="rgba(59,109,17,.07)",
            mode="lines+markers",
        )
        fig_trend.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig_trend, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB: TEAM
# ═══════════════════════════════════════════════════════════════════════════════
with tab_team:
    st.markdown('<div class="section-label">Add team member</div>', unsafe_allow_html=True)
    with st.form("add_member_form", clear_on_submit=True):
        tc1, tc2 = st.columns(2)
        with tc1:
            new_name = st.text_input("Name", placeholder="Full name")
        with tc2:
            new_role = st.text_input("Role", placeholder="e.g. Developer")

        st.markdown("**Avatar colour**")
        swatch_html = '<div class="swatches">'
        for i, c in enumerate(db.AVATAR_COLORS):
            sel_cls = "sel" if i == st.session_state.selected_color else ""
            swatch_html += (
                f'<div class="swatch {sel_cls}" style="background:{c["bg"]};'
                f'border-color:{c["fg"] if sel_cls else "transparent"}"></div>'
            )
        swatch_html += "</div>"
        st.markdown(swatch_html, unsafe_allow_html=True)

        color_names  = [f"Color {i+1}" for i in range(len(db.AVATAR_COLORS))]
        picked_color = st.radio(
            "Pick colour", color_names,
            index=st.session_state.selected_color,
            horizontal=True,
            label_visibility="collapsed",
        )
        st.session_state.selected_color = color_names.index(picked_color)

        add_btn = st.form_submit_button("Add Member", use_container_width=True)
        if add_btn and new_name.strip():
            db.add_member(new_name.strip(), new_role.strip() or "Team member", st.session_state.selected_color)
            st.success(f"Added {new_name}.")
            st.rerun()

    st.markdown("---")
    st.markdown('<div class="section-label">Current team</div>', unsafe_allow_html=True)
    all_members = db.get_members()
    cols = st.columns(min(4, len(all_members)))
    for i, m in enumerate(all_members):
        with cols[i % len(cols)]:
            st.markdown(
                f'<div style="text-align:center;border:1px solid rgba(0,0,0,.08);'
                f'border-radius:14px;padding:18px 12px;margin-bottom:10px;background:#fff">'
                f'{avatar_html(m, 52)}'
                f'<div style="font-size:14px;font-weight:600;margin-top:8px;color:#1a1a1a">{m["name"]}</div>'
                f'<div style="font-size:12px;color:#6b7280;margin-top:2px">{m["role"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button("Remove", key=f"rem_{m['id']}", use_container_width=True):
                if len(all_members) <= 1:
                    st.error("At least one member is required.")
                else:
                    db.remove_member(m["id"])
                    if st.session_state.active_member_id == m["id"]:
                        remaining = [x for x in all_members if x["id"] != m["id"]]
                        if remaining:
                            st.session_state.active_member_id = remaining[0]["id"]
                    st.rerun()
