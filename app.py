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
/* ── brand colours ── */
:root {
  --blue:      #185FA5;
  --blue-bg:   #E6F1FB;
  --blue-text: #0C447C;
  --green:     #3B6D11;
  --green-bg:  #EAF3DE;
  --green-text:#27500A;
}

/* header */
.dash-title {font-size:22px;font-weight:700;margin-bottom:0}

/* member cards grid */
.member-cards {display:flex;flex-wrap:wrap;gap:10px;margin-bottom:1rem}
.mcard {
  border:1px solid rgba(0,0,0,.12);border-radius:12px;
  padding:14px 12px;text-align:center;cursor:pointer;
  min-width:130px;flex:1 1 130px;
  transition:border-color .15s;background:#fff;
}
.mcard:hover {border-color:var(--blue)}
.mcard.active {border:2px solid var(--blue)}
.mcard .avatar {
  width:48px;height:48px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-weight:700;font-size:16px;margin:0 auto 6px;
}
.mcard .mname {font-size:14px;font-weight:600}
.mcard .mrole {font-size:12px;color:#6b7280;margin-top:2px}
.mcard .mstats{display:flex;gap:6px;justify-content:center;margin-top:8px;flex-wrap:wrap;font-size:11px;color:#9ca3af}
.mcard .mstats span{font-weight:600;color:#1a1a1a}

/* metric cards */
.metric-row {display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:1rem}
.mc {background:#f5f5f4;border-radius:8px;padding:.85rem 1rem}
.mc .lbl {font-size:12px;color:#6b7280;margin-bottom:4px}
.mc .val {font-size:22px;font-weight:700}
.mc .sub {font-size:11px;color:#9ca3af;margin-top:2px}

/* bars */
.bar-row {display:flex;align-items:center;gap:10px;margin-bottom:10px}
.bar-track {flex:1;height:8px;background:#efefed;border-radius:5px;overflow:hidden;margin-bottom:3px}
.bar-fill  {height:100%;border-radius:5px}

/* task items */
.task-item {
  display:flex;align-items:center;gap:8px;padding:6px 10px;
  border:1px solid rgba(0,0,0,.1);border-radius:8px;font-size:13px;margin-bottom:5px;
}
.task-item.done {opacity:.45;text-decoration:line-through}
.badge {
  font-size:11px;padding:2px 8px;border-radius:10px;font-weight:600;margin-left:auto;
}
.badge-company   {background:var(--blue-bg);color:var(--blue-text)}
.badge-education {background:var(--green-bg);color:var(--green-text)}

/* timer */
.timer-big {font-size:52px;font-weight:800;text-align:center;font-variant-numeric:tabular-nums;
            letter-spacing:2px;color:#1a1a1a;margin:4px 0}

/* colour swatches */
.swatches {display:flex;gap:7px;flex-wrap:wrap;margin-top:6px}
.swatch {
  width:28px;height:28px;border-radius:50%;cursor:pointer;
  border:2px solid transparent;display:inline-block;
  transition:transform .1s;
}
.swatch.sel {transform:scale(1.25);border-color:#555}

@media(max-width:600px){.metric-row{grid-template-columns:1fr 1fr}}
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
        # per-member timers: {member_id: {running, seconds, type, start_ts}}
        "timers": {},
        "selected_color": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ── helper: ensure active member is valid ─────────────────────────────────────
def get_members_cached():
    return db.get_members()

members = get_members_cached()
if not members:
    st.error("No members found – check DB.")
    st.stop()

if st.session_state.active_member_id not in [m["id"] for m in members]:
    st.session_state.active_member_id = members[0]["id"]

# ── helpers ───────────────────────────────────────────────────────────────────
def initials(name: str) -> str:
    return "".join(w[0] for w in name.split())[:2].upper()

def avatar_html(m: dict, size: int = 44) -> str:
    c = db.AVATAR_COLORS[m["color_idx"] % len(db.AVATAR_COLORS)]
    ini = initials(m["name"])
    return (
        f'<div class="avatar" style="width:{size}px;height:{size}px;'
        f'background:{c["bg"]};color:{c["fg"]}">{ini}</div>'
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
    st.markdown('<div class="dash-title">📊 Team Productivity Dashboard</div>', unsafe_allow_html=True)
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
tabs = st.tabs(["📋 Overview", "⏱ Track", "📈 Graphs", "👥 Team"])
tab_overview, tab_track, tab_graphs, tab_team = tabs

# ── MEMBER CARDS (reusable HTML) ──────────────────────────────────────────────
def member_cards_html(members, active_id, view):
    cards = []
    for m in members:
        ch = db.sum_hours(m["id"], "company", view)
        sh = db.sum_hours(m["id"], "education", view)
        tasks = db.get_tasks(m["id"])
        dt = sum(1 for t in tasks if t["done"])
        tt = len(tasks)
        active_cls = "active" if m["id"] == active_id else ""
        cards.append(
            f'<div class="mcard {active_cls}">
            f'{avatar_html(m, 44)}'
            f'<div class="mname">{m["name"]}</div>'
            f'<div class="mrole">{m["role"]}</div>'
            f'<div class="mstats">
            f'<span>{ch}h</span>&nbsp;work&nbsp;&nbsp;
            f'<span>{sh}h</span>&nbsp;study&nbsp;&nbsp;
            f'<span>{dt}/{tt}</span>&nbsp;tasks'
            f'</div></div>'
        )
    return '<div class="member-cards">' + "".join(cards) + "</div>"

# ═══════════════════════════════════════════════════════════════════════════════
# TAB: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tab_overview:
    # member picker
    st.markdown("**Select member**")
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

    am = get_active_member()
    view = st.session_state.view

    # metric cards
    ch = db.sum_hours(am["id"], "company", view)
    sh = db.sum_hours(am["id"], "education", view)
    th = round(ch + sh, 2)
    tasks = db.get_tasks(am["id"])
    dt = sum(1 for t in tasks if t["done"])
    tt = len(tasks)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Hours", f"{th}h")
    c2.metric("Company Hours", f"{ch}h")
    c3.metric("Study Hours", f"{sh}h")
    c4.metric("Tasks Done", f"{dt}/{tt}")

    # hours breakdown bars
    st.markdown("#### Hours Breakdown")
    target = 8 if view == "today" else 160
    st.caption(f"Target: {target}h/{'day' if view == 'today' else 'month'}")
    for m in members:
        mc  = db.sum_hours(m["id"], "company", view)
        ms  = db.sum_hours(m["id"], "education", view)
        tot = round(mc + ms, 2)
        cpct = min(100, round(mc / target * 100))
        spct = min(100, round(ms / target * 100))
        bold = "font-weight:700" if m["id"] == am["id"] else ""
        st.markdown(
            f"""
<div class="bar-row">
  <div style="font-size:13px;color:#6b7280;width:70px;flex-shrink:0;{bold}">{m['name']}</div>
  <div style="flex:1">
    <div class="bar-track"><div class="bar-fill" style="width:{cpct}%;background:#185FA5"></div></div>
    <div class="bar-track"><div class="bar-fill" style="width:{spct}%;background:#3B6D11"></div></div>
  </div>
  <div style="font-size:13px;width:40px;text-align:right">{tot}h</div>
</div>""",
            unsafe_allow_html=True,
        )
    st.markdown(
        '<div style="font-size:12px;color:#6b7280;margin-top:6px">'
        '<span style="display:inline-block;width:10px;height:10px;background:#185FA5;border-radius:2px;margin-right:4px"></span>Company&nbsp;&nbsp;'
        '<span style="display:inline-block;width:10px;height:10px;background:#3B6D11;border-radius:2px;margin-right:4px"></span>Study'
        "</div>",
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB: TRACK
# ═══════════════════════════════════════════════════════════════════════════════
with tab_track:
    st.markdown("### ⏱ Timers — per person")

    # show a timer block for EVERY member
    for m in members:
        mid = m["id"]
        c = db.AVATAR_COLORS[m["color_idx"] % len(db.AVATAR_COLORS)]

        with st.expander(
            f"**{m['name']}** — {m['role']}", expanded=(mid == st.session_state.active_member_id)
        ):
            # init timer state for this member if needed
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
                    "🏢 Company",
                    key=f"ttype_company_{mid}",
                    type="primary" if t_state["type"] == "company" else "secondary",
                    disabled=t_state["running"],
                ):
                    st.session_state.timers[mid]["type"] = "company"
                    st.rerun()
            with t_type_col2:
                if st.button(
                    "📚 Study",
                    key=f"ttype_edu_{mid}",
                    type="primary" if t_state["type"] == "education" else "secondary",
                    disabled=t_state["running"],
                ):
                    st.session_state.timers[mid]["type"] = "education"
                    st.rerun()

            # big timer display
            timer_color = "#185FA5" if t_state["type"] == "company" else "#3B6D11"
            st.markdown(
                f'<div class="timer-big" style="color:{timer_color}">{fmt_hms(elapsed)}</div>',
                unsafe_allow_html=True,
            )

            # running indicator
            if t_state["running"]:
                st.success("🟢 Timer running…")
            else:
                if elapsed > 0:
                    st.info(f"⏸ Paused at {fmt_hms(elapsed)}")

            # control buttons
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            with btn_col1:
                start_label = "⏸ Pause" if t_state["running"] else ("▶ Resume" if elapsed > 0 else "▶ Start")
                if st.button(start_label, key=f"start_{mid}", use_container_width=True):
                    if t_state["running"]:
                        # pause: accumulate elapsed
                        acc = int(time.time() - t_state["start_ts"])
                        st.session_state.timers[mid]["seconds"] += acc
                        st.session_state.timers[mid]["running"] = False
                        st.session_state.timers[mid]["start_ts"] = None
                    else:
                        st.session_state.timers[mid]["running"] = True
                        st.session_state.timers[mid]["start_ts"] = time.time()
                    st.rerun()

            with btn_col2:
                if st.button("🔄 Reset", key=f"reset_{mid}", use_container_width=True):
                    st.session_state.timers[mid] = {
                        "running": False, "seconds": 0,
                        "type": t_state["type"], "start_ts": None,
                    }
                    st.rerun()

            with btn_col3:
                log_disabled = elapsed < 60
                if st.button("💾 Log", key=f"log_{mid}", use_container_width=True, disabled=log_disabled):
                    # stop if running
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
                    st.success(f"✅ Logged {fmt_hms(elapsed_final)} for {m['name']}")
                    st.rerun()
                if log_disabled:
                    st.caption("Run ≥ 1 min to log")

            # ── Tasks for this member ──────────────────────────────────────
            st.markdown("---")
            st.markdown(f"**Tasks for {m['name']}**")

            # add task form
            with st.form(key=f"task_form_{mid}", clear_on_submit=True):
                tc1, tc2, tc3 = st.columns([3, 1, 1])
                with tc1:
                    task_name = st.text_input("Task description", placeholder="e.g. Fix login bug", label_visibility="collapsed")
                with tc2:
                    task_type = st.selectbox("Type", ["company", "education"], label_visibility="collapsed")
                with tc3:
                    add_task_btn = st.form_submit_button("➕ Add", use_container_width=True)
                if add_task_btn and task_name.strip():
                    db.add_task(mid, task_name.strip(), task_type)
                    st.rerun()

            # task list
            member_tasks = db.get_tasks(mid)
            if not member_tasks:
                st.caption("No tasks yet.")
            else:
                for task in member_tasks:
                    done_cls = "done" if task["done"] else ""
                    badge_cls = "badge-company" if task["task_type"] == "company" else "badge-education"
                    badge_lbl = "work" if task["task_type"] == "company" else "study"
                    col_chk, col_txt, col_del = st.columns([0.08, 0.72, 0.2])
                    with col_chk:
                        chk = st.checkbox("", value=bool(task["done"]), key=f"chk_{task['id']}", label_visibility="collapsed")
                        if chk != bool(task["done"]):
                            db.toggle_task(task["id"])
                            st.rerun()
                    with col_txt:
                        style = "text-decoration:line-through;opacity:.5" if task["done"] else ""
                        st.markdown(
                            f'<div style="font-size:13px;padding-top:5px;{style}">
                            f'{task["name"]}&nbsp;<span class="badge {badge_cls}">{badge_lbl}</span></div>',
                            unsafe_allow_html=True,
                        )
                    with col_del:
                        if st.button("🗑", key=f"del_{task['id']}", help="Delete task"):
                            db.delete_task(task["id"])
                            st.rerun()

    # ── Manual Hours Entry ────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📝 Manual Hours Entry")
    with st.form("manual_form", clear_on_submit=True):
        mc1, mc2 = st.columns(2)
        with mc1:
            manual_member = st.selectbox("Member", [m["name"] for m in members], key="man_mem")
            manual_date   = st.date_input("Date", value=date.today(), key="man_date")
        with mc2:
            company_h = st.number_input("Company hours", min_value=0.0, max_value=24.0, step=0.5, key="man_ch")
            study_h   = st.number_input("Study hours",   min_value=0.0, max_value=24.0, step=0.5, key="man_sh")
        save_btn = st.form_submit_button("💾 Save Entry", use_container_width=True)
        if save_btn:
            mid_man = members[[m["name"] for m in members].index(manual_member)]["id"]
            date_str = manual_date.isoformat()
            if company_h > 0:
                db.add_log(mid_man, date_str, "company", company_h)
            if study_h > 0:
                db.add_log(mid_man, date_str, "education", study_h)
            if company_h > 0 or study_h > 0:
                st.success("Entry saved!")
            else:
                st.warning("Enter at least one value.")

    # auto-rerun while any timer is running
    any_running = any(t.get("running") for t in st.session_state.timers.values())
    if any_running:
        time.sleep(1)
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB: GRAPHS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_graphs:
    am = get_active_member()

    st.markdown("**Viewing graphs for:**")
    g_names = [m["name"] for m in members]
    g_ids   = [m["id"]   for m in members]
    g_sel = st.radio(
        "Graph member",
        g_names,
        index=g_ids.index(am["id"]) if am["id"] in g_ids else 0,
        horizontal=True,
        label_visibility="collapsed",
    )
    gm = members[g_names.index(g_sel)]

    # last 7 days
    days = [(date.today() - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
    daily = db.get_daily_hours(gm["id"], days)

    col_bar, col_donut = st.columns(2)

    with col_bar:
        st.markdown(f"**Daily hours — {gm['name']}**")
        fig_bar = go.Figure()
        fig_bar.add_bar(
            x=[d[5:] for d in days],
            y=[daily[d]["company"] for d in days],
            name="Company",
            marker_color="#185FA5",
            marker_line_width=0,
        )
        fig_bar.add_bar(
            x=[d[5:] for d in days],
            y=[daily[d]["education"] for d in days],
            name="Study",
            marker_color="#3B6D11",
            marker_line_width=0,
        )
        fig_bar.update_layout(
            barmode="group", height=240, margin=dict(l=0,r=0,t=10,b=0),
            legend=dict(orientation="h", y=-0.25),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="rgba(0,0,0,.06)"),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_donut:
        st.markdown("**Hours split (all time)**")
        all_logs = db.get_logs(gm["id"])
        total_c = round(sum(l["hours"] for l in all_logs if l["log_type"] == "company"), 2)
        total_s = round(sum(l["hours"] for l in all_logs if l["log_type"] == "education"), 2)
        fig_donut = go.Figure(
            go.Pie(
                labels=["Company", "Study"],
                values=[total_c or 0, total_s or 0],
                hole=0.62,
                marker_colors=["#185FA5", "#3B6D11"],
            )
        )
        fig_donut.update_layout(
            height=240, margin=dict(l=0,r=0,t=10,b=0),
            legend=dict(orientation="h", y=-0.1),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    col_task_chart, col_trend = st.columns(2)

    with col_task_chart:
        st.markdown("**Task completion rate (%)**")
        tc_data = db.get_task_completion(members)
        comp_pct  = []
        study_pct = []
        for m in members:
            s = tc_data[m["id"]]
            cp = round(s["company"]["done"] / s["company"]["total"] * 100) if s["company"]["total"] else 0
            sp = round(s["education"]["done"] / s["education"]["total"] * 100) if s["education"]["total"] else 0
            comp_pct.append(cp)
            study_pct.append(sp)
        fig_tc = go.Figure()
        fig_tc.add_bar(x=[m["name"] for m in members], y=comp_pct, name="Company", marker_color="#185FA5")
        fig_tc.add_bar(x=[m["name"] for m in members], y=study_pct, name="Study",   marker_color="#3B6D11")
        fig_tc.update_layout(
            barmode="group", height=220, margin=dict(l=0,r=0,t=10,b=0),
            legend=dict(orientation="h", y=-0.3),
            yaxis=dict(range=[0,100], ticksuffix="%", gridcolor="rgba(0,0,0,.06)"),
            xaxis=dict(showgrid=False),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_tc, use_container_width=True)

    with col_trend:
        st.markdown(f"**Monthly hours trend — {gm['name']}**")
        today_d = date.today()
        months = [
            (
                (today_d.replace(day=1) - timedelta(days=1)).replace(day=1) if i > 0 else today_d.replace(day=1),
                i,
            )
            for i in range(5, -1, -1)
        ]
        # simpler: build list of (year, month) for last 6 months
        month_list = []
        d = today_d.replace(day=1)
        for _ in range(6):
            month_list.append((d.year, d.month))
            d = (d - timedelta(days=1)).replace(day=1)
        month_list.reverse()
        monthly = db.get_monthly_hours(gm["id"], month_list)
        mo_labels = [f"{datetime(y, m, 1).strftime('%b')}" for y, m in month_list]
        fig_trend = go.Figure()
        fig_trend.add_scatter(
            x=mo_labels,
            y=[monthly[(y,m)]["company"] for y,m in month_list],
            name="Company",
            line_color="#185FA5",
            fill="tozeroy",
            fillcolor="rgba(24,95,165,.08)",
            mode="lines+markers",
        )
        fig_trend.add_scatter(
            x=mo_labels,
            y=[monthly[(y,m)]["education"] for y,m in month_list],
            name="Study",
            line_color="#3B6D11",
            fill="tozeroy",
            fillcolor="rgba(59,109,17,.08)",
            mode="lines+markers",
        )
        fig_trend.update_layout(
            height=220, margin=dict(l=0,r=0,t=10,b=0),
            legend=dict(orientation="h", y=-0.3),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="rgba(0,0,0,.06)"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_trend, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB: TEAM
# ═══════════════════════════════════════════════════════════════════════════════
with tab_team:
    st.markdown("### Add Team Member")
    with st.form("add_member_form", clear_on_submit=True):
        tc1, tc2 = st.columns(2)
        with tc1:
            new_name = st.text_input("Name", placeholder="Full name")
        with tc2:
            new_role = st.text_input("Role", placeholder="e.g. Developer")

        # colour swatches
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

        # colour radio (hidden label)
        color_names = [f"Color {i+1}" for i in range(len(db.AVATAR_COLORS))]
        picked_color = st.radio(
            "Pick colour",
            color_names,
            index=st.session_state.selected_color,
            horizontal=True,
            label_visibility="collapsed",
        )
        st.session_state.selected_color = color_names.index(picked_color)

        add_btn = st.form_submit_button("��� Add Member", use_container_width=True)
        if add_btn and new_name.strip():
            db.add_member(new_name.strip(), new_role.strip() or "Team member", st.session_state.selected_color)
            st.success(f"Added {new_name}!")
            st.rerun()

    st.markdown("---")
    st.markdown("### Current Team")
    all_members = db.get_members()
    cols = st.columns(min(4, len(all_members)))
    for i, m in enumerate(all_members):
        c2 = db.AVATAR_COLORS[m["color_idx"] % len(db.AVATAR_COLORS)]
        with cols[i % len(cols)]:
            st.markdown(
                f'<div style="text-align:center;border:1px solid rgba(0,0,0,.1);'
                f'border-radius:12px;padding:16px 12px;margin-bottom:10px">'
                f'{avatar_html(m, 52)}'
                f'<div style="font-size:14px;font-weight:600;margin-top:6px">{m["name"]}</div>'
                f'<div style="font-size:12px;color:#6b7280">{m["role"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button("🗑 Remove", key=f"rem_{m['id']}", use_container_width=True):
                if len(all_members) <= 1:
                    st.error("Need at least one member.")
                else:
                    db.remove_member(m["id"])
                    if st.session_state.active_member_id == m["id"]:
                        remaining = [x for x in all_members if x["id"] != m["id"]]
                        if remaining:
                            st.session_state.active_member_id = remaining[0]["id"]
                    st.rerun()
