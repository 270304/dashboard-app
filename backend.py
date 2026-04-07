"""
backend.py — SQLite persistence layer for the Team Productivity Dashboard
"""
import sqlite3
import json
from datetime import date, datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "dashboard.db"

AVATAR_COLORS = [
    {"bg": "#E6F1FB", "fg": "#0C447C"},
    {"bg": "#EAF3DE", "fg": "#27500A"},
    {"bg": "#FAEEDA", "fg": "#633806"},
    {"bg": "#FAECE7", "fg": "#712B13"},
    {"bg": "#EEEDFE", "fg": "#3C3489"},
    {"bg": "#E1F5EE", "fg": "#085041"},
    {"bg": "#FBEAF0", "fg": "#72243E"},
    {"bg": "#F1EFE8", "fg": "#444441"},
]

DEFAULT_MEMBERS = [
    {"name": "Alice",   "role": "Developer", "color_idx": 0},
    {"name": "Bob",     "role": "Designer",  "color_idx": 1},
    {"name": "Charlie", "role": "Analyst",   "color_idx": 2},
    {"name": "Diana",   "role": "Manager",   "color_idx": 3},
]


# ── Connection ────────────────────────────────────────────────────────────────

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# ── Schema ────────────────────────────────────────────────────────────────────

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS members (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT    NOT NULL,
            role      TEXT    NOT NULL DEFAULT 'Team member',
            color_idx INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT (date('now'))
        );

        CREATE TABLE IF NOT EXISTS logs (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
            log_date  TEXT    NOT NULL,   -- ISO date  YYYY-MM-DD
            log_type  TEXT    NOT NULL,   -- 'company' | 'education'
            hours     REAL    NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
            name      TEXT    NOT NULL,
            task_type TEXT    NOT NULL DEFAULT 'company',
            done      INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS timer_sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id   INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
            timer_type  TEXT    NOT NULL,
            seconds     INTEGER NOT NULL,
            logged_at   TEXT DEFAULT (datetime('now'))
        );
    """)

    # seed default members once
    if c.execute("SELECT COUNT(*) FROM members").fetchone()[0] == 0:
        for m in DEFAULT_MEMBERS:
            c.execute(
                "INSERT INTO members (name, role, color_idx) VALUES (?,?,?)",
                (m["name"], m["role"], m["color_idx"]),
            )
    conn.commit()
    conn.close()


# ── Members ───────────────────────────────────────────────────────────────────

def get_members() -> list[dict]:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM members ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_member(name: str, role: str, color_idx: int) -> int:
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO members (name, role, color_idx) VALUES (?,?,?)",
        (name, role, color_idx),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def remove_member(member_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM members WHERE id=?", (member_id,))
    conn.commit()
    conn.close()


# ── Logs ──────────────────────────────────────────────────────────────────────

def add_log(member_id: int, log_date: str, log_type: str, hours: float):
    conn = get_conn()
    conn.execute(
        "INSERT INTO logs (member_id, log_date, log_type, hours) VALUES (?,?,?,?)",
        (member_id, log_date, log_type, round(hours, 2)),
    )
    conn.commit()
    conn.close()


def get_logs(member_id: int | None = None) -> list[dict]:
    conn = get_conn()
    if member_id:
        rows = conn.execute(
            "SELECT * FROM logs WHERE member_id=? ORDER BY log_date DESC", (member_id,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM logs ORDER BY log_date DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_logs_for_view(member_id: int, view: str) -> list[dict]:
    """Filter logs by 'today' or 'month'."""
    today_str = date.today().isoformat()
    conn = get_conn()
    if view == "today":
        rows = conn.execute(
            "SELECT * FROM logs WHERE member_id=? AND log_date=?",
            (member_id, today_str),
        ).fetchall()
    else:
        month_start = today_str[:8] + "01"
        rows = conn.execute(
            "SELECT * FROM logs WHERE member_id=? AND log_date>=?",
            (member_id, month_start),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def sum_hours(member_id: int, log_type: str, view: str) -> float:
    logs = get_logs_for_view(member_id, view)
    return round(sum(l["hours"] for l in logs if l["log_type"] == log_type), 2)


# ── Tasks ─────────────────────────────────────────────────────────────────────

def get_tasks(member_id: int) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE member_id=? ORDER BY id DESC", (member_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_task(member_id: int, name: str, task_type: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO tasks (member_id, name, task_type) VALUES (?,?,?)",
        (member_id, name, task_type),
    )
    conn.commit()
    conn.close()


def toggle_task(task_id: int):
    conn = get_conn()
    conn.execute("UPDATE tasks SET done = 1-done WHERE id=?", (task_id,))
    conn.commit()
    conn.close()


def delete_task(task_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()


# ── Timer sessions ────────────────────────────────────────────────────────────

def log_timer_session(member_id: int, timer_type: str, seconds: int):
    hours = round(seconds / 3600, 2)
    today_str = date.today().isoformat()
    conn = get_conn()
    conn.execute(
        "INSERT INTO timer_sessions (member_id, timer_type, seconds) VALUES (?,?,?)",
        (member_id, timer_type, seconds),
    )
    conn.execute(
        "INSERT INTO logs (member_id, log_date, log_type, hours) VALUES (?,?,?,?)",
        (member_id, today_str, timer_type, hours),
    )
    conn.commit()
    conn.close()


# ── Analytics helpers ─────────────────────────────────────────────────────────

def get_daily_hours(member_id: int, days: list[str]) -> dict:
    """Return {date: {company: h, education: h}} for the given date list."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT log_date, log_type, SUM(hours) as h FROM logs "
        "WHERE member_id=? AND log_date IN ({}) GROUP BY log_date, log_type".format(
            ",".join("?" * len(days))
        ),
        (member_id, *days),
    ).fetchall()
    conn.close()
    result = {d: {"company": 0.0, "education": 0.0} for d in days}
    for r in rows:
        result[r["log_date"]][r["log_type"]] = round(r["h"], 2)
    return result


def get_monthly_hours(member_id: int, months: list[tuple[int, int]]) -> dict:
    """months = list of (year, month). Returns {(y,m): {company, education}}."""
    conn = get_conn()
    result = {m: {"company": 0.0, "education": 0.0} for m in months}
    for y, m in months:
        month_str = f"{y:04d}-{m:02d}"
        rows = conn.execute(
            "SELECT log_type, SUM(hours) as h FROM logs "
            "WHERE member_id=? AND log_date LIKE ? GROUP BY log_type",
            (member_id, f"{month_str}%"),
        ).fetchall()
        for r in rows:
            result[(y, m)][r["log_type"]] = round(r["h"], 2)
    conn.close()
    return result


def get_task_completion(members: list[dict]) -> dict:
    """Return per-member task completion rates."""
    conn = get_conn()
    result = {}
    for m in members:
        mid = m["id"]
        rows = conn.execute(
            "SELECT task_type, done, COUNT(*) as cnt FROM tasks "
            "WHERE member_id=? GROUP BY task_type, done",
            (mid,),
        ).fetchall()
        stats = {"company": {"done": 0, "total": 0}, "education": {"done": 0, "total": 0}}
        for r in rows:
            t = r["task_type"]
            if t in stats:
                stats[t]["total"] += r["cnt"]
                if r["done"]:
                    stats[t]["done"] += r["cnt"]
        result[mid] = stats
    conn.close()
    return result
