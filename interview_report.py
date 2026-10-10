import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
import re
import io

DB_FILE = "students.db"
COURSES = ["Data Science", "Full Stack", "UI/UX Designer"]
COURSE_OPTIONS = ["Select Course", "All Courses"] + COURSES

st.set_page_config(
    page_title="Student Performance Management",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- CSS (Dark / Black Theme) --------------------
st.markdown("""
<style>
    /* ===== Global ===== */
    html, body, [class*="css"] {
        font-family: 'Poppins', 'Segoe UI', 'Inter', sans-serif;
    }
    .stApp {
        background: radial-gradient(circle at top left, #17181d 0%, #0b0c10 45%, #000000 100%);
    }
    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 3rem;
        max-width: 1300px;
    }
    /* Default text color across the app */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp li {
        color: #e5e7eb;
    }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
        color: #f8fafc;
    }
    .stApp .stCaption, .stApp small {
        color: #94a3b8 !important;
    }

    /* ===== Sidebar ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #000000 0%, #0f0f13 55%, #16161c 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.12) !important;
        margin: 14px 0;
    }
    [data-testid="stSidebar"] h2 {
        font-weight: 800;
        letter-spacing: .02em;
    }

    /* Sidebar nav buttons — force solid backgrounds so text is always readable */
    [data-testid="stSidebar"] div.stButton > button {
        width: 100%;
        text-align: left;
        border-radius: 12px !important;
        padding: 10px 16px !important;
        font-weight: 600 !important;
        font-size: 0.98rem !important;
        border: 1px solid rgba(255,255,255,0.14) !important;
        background: rgba(255,255,255,0.06) !important;
        color: #e2e8f0 !important;
        transition: all .15s ease-in-out;
        margin-bottom: 4px;
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        background: rgba(99,102,241,0.35) !important;
        border-color: rgba(99,102,241,0.7) !important;
        color: #ffffff !important;
        transform: translateX(2px);
    }
    [data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
        border: 1px solid #818cf8 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(99,102,241,0.45);
    }
    [data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
        background: rgba(255,255,255,0.06) !important;
        color: #e2e8f0 !important;
    }

    /* Sidebar info/status boxes */
    [data-testid="stSidebar"] div[data-testid="stAlertContainer"] {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
    }

    /* ===== Header ===== */
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.1rem;
        background: linear-gradient(90deg, #a5b4fc, #818cf8, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .subtitle {
        color: #94a3b8 !important;
        font-size: 1.02rem;
        margin-bottom: 1.6rem;
        font-weight: 500;
    }

    /* ===== Stat / metric cards ===== */
    .stat-card {
        background: #131417;
        padding: 20px 22px;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 6px 20px rgba(0,0,0,.5);
        min-height: 120px;
        transition: transform .15s ease, box-shadow .15s ease;
    }
    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(99,102,241,.25);
        border-color: rgba(99,102,241,0.4);
    }
    .stat-label {
        color: #94a3b8;
        font-size: .88rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .04em;
    }
    .stat-value {
        color: #f8fafc;
        font-size: 2.1rem;
        font-weight: 800;
        margin-top: 6px;
    }

    /* ===== Section cards ===== */
    .section-card {
        background: #131417;
        padding: 24px 26px;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 6px 20px rgba(0,0,0,.5);
        margin-bottom: 22px;
        color: #e5e7eb;
    }
    .section-card h2, .section-card h3 {
        color: #f8fafc;
    }
    .section-card p, .section-card b {
        color: #e5e7eb;
    }

    /* ===== Grade badges ===== */
    .grade-excellent {
        background: rgba(34,197,94,0.18);
        color: #4ade80;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        border: 1px solid rgba(74,222,128,0.5);
    }
    .grade-good {
        background: rgba(59,130,246,0.18);
        color: #60a5fa;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        border: 1px solid rgba(96,165,250,0.5);
    }
    .grade-average {
        background: rgba(245,158,11,0.18);
        color: #fbbf24;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        border: 1px solid rgba(251,191,36,0.5);
    }
    .grade-low {
        background: rgba(239,68,68,0.18);
        color: #f87171;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        border: 1px solid rgba(248,113,113,0.5);
    }

    /* ===== Buttons (main area) ===== */
    div.stButton > button {
        border-radius: 10px;
        font-weight: 650;
        background: #1c1d22;
        color: #e5e7eb;
        border: 1px solid rgba(255,255,255,0.12);
    }
    div.stButton > button:hover {
        border-color: rgba(99,102,241,0.6);
        color: #ffffff;
    }
    .main .block-container div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #4f46e5, #6366f1);
        border: none;
        color: white !important;
        box-shadow: 0 4px 14px rgba(79,70,229,.45);
    }
    .main .block-container div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(90deg, #4338ca, #4f46e5);
    }

    /* ===== Profile card ===== */
    .profile-card {
        background: linear-gradient(135deg, #000000, #1e1b3a 60%, #4338ca);
        color: white !important;
        padding: 26px;
        border-radius: 20px;
        margin-bottom: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,.6);
        border: 1px solid rgba(255,255,255,0.08);
    }
    .profile-card * {
        color: white !important;
    }

    /* ===== Podium / top performer cards ===== */
    .podium-card {
        text-align: center;
        border-radius: 18px;
    }

    /* ===== Tabs ===== */
    button[data-baseweb="tab"] {
        font-weight: 650;
        font-size: 0.98rem;
        color: #94a3b8 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #f8fafc !important;
    }
    div[data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid rgba(255,255,255,0.1) !important;
    }
    div[data-baseweb="tab-highlight"] {
        background-color: #6366f1 !important;
    }

    /* ===== Expander ===== */
    details {
        background: #131417 !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }
    summary {
        color: #f8fafc !important;
    }

    /* ===== Dataframe ===== */
    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.08);
    }

    /* ===== Metrics (native st.metric) ===== */
    div[data-testid="stMetric"] {
        background: #131417;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 12px 14px;
        box-shadow: 0 4px 14px rgba(0,0,0,.5);
    }
    div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }

    /* ===== Inputs ===== */
    .stTextInput input, .stNumberInput input {
        border-radius: 10px !important;
        background-color: #131417 !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
    }
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 10px !important;
        background-color: #131417 !important;
    }
    .stSelectbox div[data-baseweb="select"] * {
        color: #f8fafc !important;
    }
    div[data-baseweb="popover"] {
        background-color: #131417 !important;
    }
    ul[role="listbox"] {
        background-color: #131417 !important;
    }
    li[role="option"] {
        color: #e5e7eb !important;
    }
    .stTextInput label, .stNumberInput label, .stSelectbox label {
        color: #cbd5e1 !important;
    }

    /* ===== Forms ===== */
    div[data-testid="stForm"] {
        background: #101013;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 18px;
    }

    /* ===== Alerts (info/success/warning/error) keep readable on dark bg ===== */
    div[data-testid="stAlertContainer"] {
        border-radius: 12px;
    }

    /* ===== Checkbox ===== */
    .stCheckbox label {
        color: #e5e7eb !important;
    }

    hr {
        border-color: rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)


# -------------------- Database --------------------
def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            mobile TEXT,
            course TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            cv REAL,
            confidence REAL,
            knowledge REAL,
            conversion REAL,
            updated_at TEXT,
            FOREIGN KEY(student_id) REFERENCES students(student_id)
        )
    """)

    # Persistent course-wise counters. IDs are generated as:
    # Data Science -> DS-001, DS-002...
    # Full Stack -> FS-001, FS-002...
    # UI/UX Designer -> UX-001, UX-002...
    cur.execute("""
        CREATE TABLE IF NOT EXISTS course_id_counter (
            course TEXT PRIMARY KEY,
            next_number INTEGER NOT NULL
        )
    """)

    prefixes = {"Data Science": "DS", "Full Stack": "FS", "UI/UX Designer": "UX"}
    for course, prefix in prefixes.items():
        row = cur.execute(
            "SELECT next_number FROM course_id_counter WHERE course=?",
            (course,)
        ).fetchone()
        if row is None:
            existing = cur.execute(
                "SELECT student_id FROM students WHERE course=?",
                (course,)
            ).fetchall()
            max_num = 0
            for r in existing:
                m = re.fullmatch(rf"{prefix}-(\d+)", str(r[0]).strip(), re.IGNORECASE)
                if m:
                    max_num = max(max_num, int(m.group(1)))
            cur.execute(
                "INSERT INTO course_id_counter (course, next_number) VALUES (?, ?)",
                (course, max_num + 1)
            )

    conn.commit()
    conn.close()


def get_students():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT
            s.student_id,
            s.name,
            s.email,
            s.mobile,
            s.course,
            s.created_at,
            e.cv,
            e.confidence,
            e.knowledge,
            e.conversion,
            e.updated_at
        FROM students s
        LEFT JOIN evaluations e ON s.student_id = e.student_id
        ORDER BY s.name COLLATE NOCASE
    """, conn)
    conn.close()
    return df


def get_course_prefix(course):
    return {
        "Data Science": "DS",
        "Full Stack": "FS",
        "UI/UX Designer": "UX",
    }.get(course, "STU")


def get_next_student_id(course):
    """Return the next ID for the selected course without consuming it."""
    prefix = get_course_prefix(course)
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT next_number FROM course_id_counter WHERE course=?",
            (course,)
        ).fetchone()
        if row is None:
            existing = conn.execute(
                "SELECT student_id FROM students WHERE course=?",
                (course,)
            ).fetchall()
            max_num = 0
            for r in existing:
                m = re.fullmatch(rf"{prefix}-(\d+)", str(r[0]).strip(), re.IGNORECASE)
                if m:
                    max_num = max(max_num, int(m.group(1)))
            return f"{prefix}-{max_num + 1:03d}"
        return f"{prefix}-{int(row['next_number']):03d}"
    finally:
        conn.close()


def add_student(student_id, name, email, mobile, course):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO students
            (student_id, name, email, mobile, course, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            student_id.strip(),
            name.strip(),
            email.strip(),
            mobile.strip(),
            course.strip(),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        # Consume the course-specific ID only after the student is inserted.
        current = conn.execute(
            "SELECT next_number FROM course_id_counter WHERE course=?",
            (course,)
        ).fetchone()
        if current is not None:
            conn.execute(
                "UPDATE course_id_counter SET next_number=? WHERE course=?",
                (int(current["next_number"]) + 1, course)
            )

        conn.commit()
        return True, "Student added successfully."
    except sqlite3.IntegrityError:
        conn.rollback()
        return False, "Student ID already exists."
    finally:
        conn.close()


def update_student(original_id, student_id, name, email, mobile, course):
    conn = get_connection()
    try:
        conn.execute("""
            UPDATE students
            SET student_id=?, name=?, email=?, mobile=?
                ,course=?
            WHERE student_id=?
        """, (
            student_id.strip(), name.strip(), email.strip(),
            mobile.strip(), course.strip(), original_id
        ))

        if original_id != student_id:
            conn.execute("""
                UPDATE evaluations
                SET student_id=?
                WHERE student_id=?
            """, (student_id.strip(), original_id))

        conn.commit()
        return True, "Student updated successfully."
    except sqlite3.IntegrityError:
        return False, "New Student ID already exists."
    finally:
        conn.close()


def delete_student(student_id):
    conn = get_connection()
    conn.execute("DELETE FROM evaluations WHERE student_id=?", (student_id,))
    conn.execute("DELETE FROM students WHERE student_id=?", (student_id,))
    conn.commit()
    conn.close()


def save_evaluation(student_id, cv, confidence, knowledge, conversion):
    conn = get_connection()
    conn.execute("""
        INSERT INTO evaluations
        (student_id, cv, confidence, knowledge, conversion, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(student_id) DO UPDATE SET
            cv=excluded.cv,
            confidence=excluded.confidence,
            knowledge=excluded.knowledge,
            conversion=excluded.conversion,
            updated_at=excluded.updated_at
    """, (
        student_id, cv, confidence, knowledge, conversion,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()


# -------------------- Helpers --------------------
def get_grade(total):
    if total is None:
        return "Not Evaluated"
    if total >= 36:
        return "Excellent"
    if total >= 30:
        return "Very Good"
    if total >= 24:
        return "Good"
    if total >= 20:
        return "Average"
    return "Needs Improvement"


def grade_class(grade):
    if grade == "Excellent":
        return "grade-excellent"
    if grade == "Very Good" or grade == "Good":
        return "grade-good"
    if grade == "Average":
        return "grade-average"
    return "grade-low"


def prepare_dataframe(df):
    df = df.copy()

    score_cols = ["cv", "confidence", "knowledge", "conversion"]
    for col in score_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["evaluated"] = df[score_cols].notna().all(axis=1)
    df["total"] = df[score_cols].sum(axis=1, min_count=4)
    df["percentage"] = (df["total"] / 40 * 100).round(1)
    df["grade"] = df["total"].apply(get_grade)

    evaluated = df["total"].notna()
    df["rank"] = None
    if evaluated.any():
        ranks = df.loc[evaluated, "total"].rank(
            method="min", ascending=False
        ).astype(int)
        df.loc[evaluated, "rank"] = ranks

    return df


def valid_email(email):
    if not email:
        return True
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None


def valid_mobile(mobile):
    if not mobile:
        return True
    return re.match(r"^[0-9]{10}$", mobile) is not None


def metric_card(label, value, icon):
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">{icon} {label}</div>
        <div class="stat-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


PLOTLY_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e5e7eb"),
)


# -------------------- App --------------------
init_db()

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "edit_student" not in st.session_state:
    st.session_state.edit_student = None

if "selected_student" not in st.session_state:
    st.session_state.selected_student = None


# -------------------- Sidebar --------------------
with st.sidebar:
    st.markdown("## 🎓 Student System")
    st.caption("Student Performance Management")
    st.divider()

    st.markdown("### 🎯 Select Course")
    selected_course = st.selectbox(
        "Course",
        COURSE_OPTIONS,
        index=0,
        key="global_course"
    )
    st.caption("Choose a course first. Student, Evaluation and Analytics data will be shown course-wise.")

    st.divider()

    pages = {
        "🏠 Dashboard": "Dashboard",
        "👨‍🎓 Students": "Students",
        "📝 Evaluation": "Evaluation",
        "📊 Analytics": "Analytics",
    }

    for label, page_name in pages.items():
        if st.button(
            label,
            use_container_width=True,
            type="primary" if st.session_state.page == page_name else "secondary"
        ):
            st.session_state.page = page_name
            st.rerun()

    st.divider()

    raw_students = get_students()
    evaluated_count = 0
    if not raw_students.empty:
        temp = prepare_dataframe(raw_students)
        evaluated_count = int(temp["evaluated"].sum())

    st.markdown("### System Status")
    st.info(f"👥 Students: **{len(raw_students)}**")
    st.info(f"📝 Evaluated: **{evaluated_count}**")


# -------------------- Header --------------------
st.markdown(
    '<div class="main-title">🎓 Student Performance Management</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Manage students, evaluate performance, and track results.</div>',
    unsafe_allow_html=True
)


# -------------------- Dashboard --------------------
if st.session_state.page == "Dashboard":
    df = prepare_dataframe(get_students())
    if selected_course not in ("Select Course", "All Courses"):
        df = df[df["course"].fillna("") == selected_course].copy()

    total_students = len(df)
    evaluated = int(df["evaluated"].sum()) if not df.empty else 0
    highest = df["total"].max() if not df.empty and df["total"].notna().any() else 0
    average = df["total"].mean() if not df.empty and df["total"].notna().any() else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total Students", f"{total_students}", "👥")
    with c2:
        metric_card("Evaluated", evaluated, "📝")
    with c3:
        metric_card("Highest Score", f"{highest:.1f}/40" if highest else "—", "🏆")
    with c4:
        metric_card("Average Score", f"{average:.1f}/40" if average else "—", "📈")

    st.markdown("### 🏆 Top Performers")

    if df.empty:
        st.markdown("""
        <div class="section-card">
            <h3>👋 No students yet</h3>
            <p>Add your first student from the <b>Students</b> section.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        top = df[df["total"].notna()].sort_values(
            ["total", "name"], ascending=[False, True]
        ).head(3)

        if top.empty:
            st.info("No evaluations available yet.")
        else:
            podium_colors = [
                "linear-gradient(135deg, #78350f, #f59e0b)",
                "linear-gradient(135deg, #334155, #94a3b8)",
                "linear-gradient(135deg, #7c2d12, #ea580c)",
            ]
            cols = st.columns(3)
            medals = ["🥇", "🥈", "🥉"]
            for i, (_, row) in enumerate(top.iterrows()):
                with cols[i]:
                    st.markdown(f"""
                    <div class="section-card podium-card" style="background:{podium_colors[i]};">
                        <div style="font-size:2.4rem;">{medals[i]}</div>
                        <h3 style="color:#ffffff;margin-bottom:2px;">{row['name']}</h3>
                        <div style="font-size:1.6rem;font-weight:800;color:#ffffff;">
                            {row['total']:.1f}/40
                        </div>
                        <p style="color:#f1f5f9;font-weight:600;">{row['percentage']:.1f}% • {row['grade']}</p>
                    </div>
                    """, unsafe_allow_html=True)

    if not df.empty and df["total"].notna().any():
        st.markdown("### 📊 Score Overview")
        chart_df = df[df["total"].notna()].sort_values("total", ascending=False)
        fig = px.bar(
            chart_df,
            x="name",
            y="total",
            text="total",
            labels={"name": "Student", "total": "Total / 40"},
            title="Student Total Scores",
            color="total",
            color_continuous_scale=["#f87171", "#fbbf24", "#4ade80"],
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            height=420,
            margin=dict(l=20, r=20, t=60, b=20),
            coloraxis_showscale=False,
            **PLOTLY_LAYOUT,
        )
        fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)")
        fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)")
        st.plotly_chart(fig, use_container_width=True)


# -------------------- Students --------------------
elif st.session_state.page == "Students":
    st.markdown("## 👨‍🎓 Student Management")

    df = prepare_dataframe(get_students())
    if selected_course not in ("Select Course", "All Courses"):
        df = df[df["course"].fillna("") == selected_course].copy()

    add_tab, edit_tab, list_tab = st.tabs(
        ["➕ Add Student", "✏️ Edit Student", "📋 Student List"]
    )

    with add_tab:
        with st.form("add_student_form", clear_on_submit=True):
            a, b = st.columns(2)

            with a:
                student_id = st.text_input(
                    "Student ID",
                    value=get_next_student_id(selected_course) if selected_course not in ("Select Course", "All Courses") else "Select a course first",
                    disabled=True,
                    help="Student ID is generated automatically course-wise: DS-001, FS-001, UX-001, ..."
                )
                name = st.text_input(
                    "Student Name *",
                    placeholder="Enter full name"
                )
                email = st.text_input(
                    "Email",
                    placeholder="student@example.com"
                )

            with b:
                mobile = st.text_input(
                    "Mobile Number",
                    placeholder="10 digit mobile number"
                )
                if selected_course in ("Select Course", "All Courses"):
                    st.warning("Please select a specific course from the Course selector before adding a student.")
                    course = ""
                else:
                    st.text_input(
                        "Course / Class",
                        value=selected_course,
                        disabled=True,
                        help="Course is selected from the Course selector above."
                    )
                    course = selected_course

            submitted = st.form_submit_button(
                "➕ Add Student",
                type="primary",
                use_container_width=True
            )

            if submitted:
                if selected_course in ("Select Course", "All Courses"):
                    st.error("Please select Data Science, Full Stack, or UI/UX Designer before adding a student.")
                elif not name.strip():
                    st.error("Student Name is required.")
                elif not valid_email(email.strip()):
                    st.error("Please enter a valid email.")
                elif not valid_mobile(mobile.strip()):
                    st.error("Mobile number must contain exactly 10 digits.")
                else:
                    ok, msg = add_student(
                        student_id, name, email, mobile, course
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with edit_tab:
        if df.empty:
            st.info("No students available to edit.")
        else:
            selected = st.selectbox(
                "Select Student",
                df["student_id"].tolist(),
                format_func=lambda x: (
                    f"{x} — "
                    f"{df.loc[df['student_id'] == x, 'name'].iloc[0]}"
                )
            )

            row = df[df["student_id"] == selected].iloc[0]

            with st.form("edit_student_form"):
                a, b = st.columns(2)
                with a:
                    new_id = st.text_input("Student ID", value=row["student_id"], disabled=True)
                    new_name = st.text_input("Student Name *", value=row["name"])
                    new_email = st.text_input("Email", value=row["email"] or "")
                with b:
                    new_mobile = st.text_input("Mobile", value=row["mobile"] or "")
                    new_course = st.text_input("Course / Class", value=row["course"] or "", disabled=True)

                update_btn = st.form_submit_button(
                    "💾 Save Changes",
                    type="primary",
                    use_container_width=True
                )

                if update_btn:
                    if not new_id.strip() or not new_name.strip():
                        st.error("Student ID and Student Name are required.")
                    elif not valid_email(new_email.strip()):
                        st.error("Please enter a valid email.")
                    elif not valid_mobile(new_mobile.strip()):
                        st.error("Mobile number must contain exactly 10 digits.")
                    else:
                        ok, msg = update_student(
                            selected,
                            new_id,
                            new_name,
                            new_email,
                            new_mobile,
                            new_course
                        )
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    with list_tab:
        if df.empty:
            st.info("No students added yet.")
        else:
            st.markdown("### 🔎 Search & Filter")

            q1, q2, q3 = st.columns([2, 1, 1])
            with q1:
                search = st.text_input(
                    "Search",
                    placeholder="Search by name or Student ID..."
                )
            with q2:
                grade_filter = st.selectbox(
                    "Grade",
                    ["All", "Excellent", "Very Good", "Good", "Average",
                     "Needs Improvement", "Not Evaluated"]
                )
            with q3:
                status_filter = st.selectbox(
                    "Status",
                    ["All", "Evaluated", "Pending"]
                )

            filtered = df.copy()

            if search:
                s = search.lower()
                filtered = filtered[
                    filtered["name"].str.lower().str.contains(s, na=False)
                    | filtered["student_id"].str.lower().str.contains(s, na=False)
                ]

            if grade_filter != "All":
                filtered = filtered[filtered["grade"] == grade_filter]

            if status_filter == "Evaluated":
                filtered = filtered[filtered["evaluated"]]
            elif status_filter == "Pending":
                filtered = filtered[~filtered["evaluated"]]

            sort_by = st.selectbox(
                "Sort By",
                ["Rank", "Name", "Total", "Percentage",
                 "CV", "Confidence", "Knowledge", "Conversion"]
            )

            sort_map = {
                "Rank": "rank",
                "Name": "name",
                "Total": "total",
                "Percentage": "percentage",
                "CV": "cv",
                "Confidence": "confidence",
                "Knowledge": "knowledge",
                "Conversion": "conversion",
            }

            sort_col = sort_map[sort_by]
            if sort_col == "name":
                filtered = filtered.sort_values(
                    sort_col, ascending=True, na_position="last"
                )
            else:
                filtered = filtered.sort_values(
                    sort_col, ascending=False, na_position="last"
                )

            st.markdown("### 📋 Student Performance Table")

            display = filtered[[
                "rank", "student_id", "name", "cv", "confidence",
                "knowledge", "conversion", "total", "percentage", "grade"
            ]].copy()

            display.columns = [
                "Rank", "Student ID", "Student Name", "CV /10",
                "Confidence /10", "Knowledge /10", "Conversion /10",
                "Total /40", "Percentage", "Grade"
            ]

            for col in ["CV /10", "Confidence /10", "Knowledge /10"]:
                display[col] = display[col].apply(
                    lambda x: f"{x:.1f}" if pd.notna(x) else "—"
                )
            display["Conversion /10"] = display["Conversion /10"].apply(
                lambda x: f"{x:.1f}" if pd.notna(x) else "—"
            )
            display["Total /40"] = display["Total /40"].apply(
                lambda x: f"{x:.1f}" if pd.notna(x) else "—"
            )
            display["Percentage"] = display["Percentage"].apply(
                lambda x: f"{x:.1f}%" if pd.notna(x) else "—"
            )
            display["Rank"] = display["Rank"].apply(
                lambda x: f"#{int(x)}" if pd.notna(x) else "—"
            )

            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True
            )

            st.markdown("### 🗑️ Delete Student")
            delete_student_id = st.selectbox(
                "Select student to delete",
                filtered["student_id"].tolist(),
                format_func=lambda x: (
                    f"{x} — "
                    f"{filtered.loc[filtered['student_id'] == x, 'name'].iloc[0]}"
                )
            )

            confirm_delete = st.checkbox(
                "I confirm that I want to permanently delete this student."
            )

            if st.button(
                "🗑️ Delete Selected Student",
                type="secondary",
                disabled=not confirm_delete
            ):
                delete_student(delete_student_id)
                st.success("Student deleted successfully.")
                st.rerun()

            st.markdown("### 👤 Student Details")
            detail_id = st.selectbox(
                "View Student",
                filtered["student_id"].tolist(),
                key="detail_student"
            )
            detail = filtered[filtered["student_id"] == detail_id].iloc[0]

            st.markdown(f"""
            <div class="profile-card">
                <h2>{detail['name']}</h2>
                <p>Student ID: <b>{detail['student_id']}</b></p>
                <p>Course: <b>{detail['course'] or '—'}</b></p>
                <p>Email: <b>{detail['email'] or '—'}</b></p>
                <p>Mobile: <b>{detail['mobile'] or '—'}</b></p>
            </div>
            """, unsafe_allow_html=True)

            if detail["evaluated"]:
                grade_html = f'<span class="{grade_class(detail["grade"])}">{detail["grade"]}</span>'
                st.markdown(
                    f"**Total:** {detail['total']:.1f}/40 &nbsp;|&nbsp; "
                    f"**Percentage:** {detail['percentage']:.1f}% &nbsp;|&nbsp; "
                    f"**Grade:** {grade_html} &nbsp;|&nbsp; "
                    f"**Rank:** #{int(detail['rank'])}",
                    unsafe_allow_html=True
                )

                pc1, pc2 = st.columns(2)
                with pc1:
                    st.progress(min(float(detail["cv"]) / 10, 1.0))
                    st.caption(f"CV — {detail['cv']:.1f}/10")
                    st.progress(min(float(detail["confidence"]) / 10, 1.0))
                    st.caption(f"Confidence — {detail['confidence']:.1f}/10")
                with pc2:
                    st.progress(min(float(detail["knowledge"]) / 10, 1.0))
                    st.caption(f"Knowledge — {detail['knowledge']:.1f}/10")
                    st.progress(min(float(detail["conversion"]) / 10, 1.0))
                    st.caption(f"Conversion — {detail['conversion']:.1f}/10")
            else:
                st.warning("📝 Evaluation pending for this student.")


# -------------------- Evaluation --------------------
elif st.session_state.page == "Evaluation":
    st.markdown("## 📝 Student Evaluation")

    df = prepare_dataframe(get_students())
    if selected_course not in ("Select Course", "All Courses"):
        df = df[df["course"].fillna("") == selected_course].copy()

    if df.empty:
        st.info("Add students first from the Students section.")
    else:
        selected = st.selectbox(
            "Select Student",
            df["student_id"].tolist(),
            format_func=lambda x: (
                f"{x} — "
                f"{df.loc[df['student_id'] == x, 'name'].iloc[0]}"
            )
        )

        row = df[df["student_id"] == selected].iloc[0]

        st.markdown(f"""
        <div class="section-card">
            <h2>👤 {row['name']}</h2>
            <p><b>Student ID:</b> {row['student_id']} &nbsp;&nbsp;
            <b>Course:</b> {row['course'] or '—'}</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("evaluation_form"):
            st.markdown("### Enter Marks — Each criterion is out of 10")

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                cv = st.number_input(
                    "📄 CV / 10",
                    min_value=0.0,
                    max_value=10.0,
                    value=float(row["cv"]) if pd.notna(row["cv"]) else 0.0,
                    step=0.5
                )
            with c2:
                confidence = st.number_input(
                    "💬 Confidence / 10",
                    min_value=0.0,
                    max_value=10.0,
                    value=float(row["confidence"]) if pd.notna(row["confidence"]) else 0.0,
                    step=0.5
                )
            with c3:
                knowledge = st.number_input(
                    "🧠 Knowledge / 10",
                    min_value=0.0,
                    max_value=10.0,
                    value=float(row["knowledge"]) if pd.notna(row["knowledge"]) else 0.0,
                    step=0.5
                )
            with c4:
                conversion = st.number_input(
                    "🎯 Conversion / 10",
                    min_value=0.0,
                    max_value=10.0,
                    value=float(row["conversion"]) if pd.notna(row["conversion"]) else 0.0,
                    step=0.5
                )

            total_preview = cv + confidence + knowledge + conversion
            percentage_preview = total_preview / 40 * 100
            grade_preview = get_grade(total_preview)

            st.divider()

            p1, p2, p3 = st.columns(3)
            with p1:
                metric_card("Total Score", f"{total_preview:.1f}/40", "🏆")
            with p2:
                metric_card("Percentage", f"{percentage_preview:.1f}%", "📈")
            with p3:
                metric_card("Grade", grade_preview, "🎓")

            save_btn = st.form_submit_button(
                "💾 Save Evaluation",
                type="primary",
                use_container_width=True
            )

            if save_btn:
                save_evaluation(
                    selected,
                    cv,
                    confidence,
                    knowledge,
                    conversion
                )
                st.success("Evaluation saved successfully.")
                st.rerun()


# -------------------- Analytics --------------------
elif st.session_state.page == "Analytics":
    st.markdown("## 📊 Analytics & Performance")

    df = prepare_dataframe(get_students())
    if selected_course not in ("Select Course", "All Courses"):
        df = df[df["course"].fillna("") == selected_course].copy()
    evaluated_df = df[df["evaluated"]].copy() if not df.empty else pd.DataFrame()

    if evaluated_df.empty:
        st.info("Add students and enter evaluations to see analytics.")
    else:
        a1, a2, a3, a4 = st.columns(4)

        with a1:
            metric_card(
                "Avg CV",
                f"{evaluated_df['cv'].mean():.1f}/10",
                "📄"
            )
        with a2:
            metric_card(
                "Avg Confidence",
                f"{evaluated_df['confidence'].mean():.1f}/10",
                "💬"
            )
        with a3:
            metric_card(
                "Avg Knowledge",
                f"{evaluated_df['knowledge'].mean():.1f}/10",
                "🧠"
            )
        with a4:
            metric_card(
                "Avg Conversion",
                f"{evaluated_df['conversion'].mean():.1f}/10",
                "🎯"
            )

        st.markdown("### 📈 Student Total Score")

        chart_df = evaluated_df.sort_values("total", ascending=False)
        fig = px.bar(
            chart_df,
            x="name",
            y="total",
            text="total",
            labels={"name": "Student", "total": "Total / 40"},
            title="Total Score by Student",
            color="total",
            color_continuous_scale=["#f87171", "#fbbf24", "#4ade80"],
        )
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig.update_yaxes(range=[0, 44])
        fig.update_layout(
            height=430,
            margin=dict(l=20, r=20, t=60, b=20),
            coloraxis_showscale=False,
            **PLOTLY_LAYOUT,
        )
        fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)")
        fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 🎯 Criteria-wise Average")

        avg_data = pd.DataFrame({
            "Criteria": ["CV", "Confidence", "Knowledge", "Conversion"],
            "Average": [
                evaluated_df["cv"].mean(),
                evaluated_df["confidence"].mean(),
                evaluated_df["knowledge"].mean(),
                evaluated_df["conversion"].mean(),
            ]
        })

        fig2 = px.bar(
            avg_data,
            x="Criteria",
            y="Average",
            text="Average",
            range_y=[0, 10],
            title="Average Performance by Criteria",
            color="Criteria",
            color_discrete_sequence=["#6366f1", "#8b5cf6", "#ec4899", "#f59e0b"],
        )
        fig2.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig2.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=60, b=20),
            showlegend=False,
            **PLOTLY_LAYOUT,
        )
        fig2.update_xaxes(gridcolor="rgba(255,255,255,0.08)")
        fig2.update_yaxes(gridcolor="rgba(255,255,255,0.08)")
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### 🏅 Ranking")

        ranking = evaluated_df.sort_values(
            ["total", "name"], ascending=[False, True]
        )[[
            "rank", "student_id", "name", "total", "percentage", "grade"
        ]].copy()

        ranking.columns = [
            "Rank", "Student ID", "Student Name",
            "Total /40", "Percentage", "Grade"
        ]

        ranking["Rank"] = ranking["Rank"].apply(lambda x: f"#{int(x)}")
        ranking["Total /40"] = ranking["Total /40"].apply(
            lambda x: f"{x:.1f}"
        )
        ranking["Percentage"] = ranking["Percentage"].apply(
            lambda x: f"{x:.1f}%"
        )

        st.dataframe(
            ranking,
            use_container_width=True,
            hide_index=True
        )


# -------------------- Export --------------------
st.divider()

with st.expander("📥 Export Student Data"):
    export_df = prepare_dataframe(get_students())
    if selected_course not in ("Select Course", "All Courses"):
        export_df = export_df[export_df["course"].fillna("") == selected_course].copy()

    if export_df.empty:
        st.info("No student data available for export.")
    else:
        export = export_df[[
            "rank", "student_id", "name", "email", "mobile", "course",
            "cv", "confidence", "knowledge", "conversion",
            "total", "percentage", "grade"
        ]].copy()

        export.columns = [
            "Rank", "Student ID", "Name", "Email", "Mobile", "Course",
            "CV /10", "Confidence /10", "Knowledge /10", "Conversion /10",
            "Total /40", "Percentage", "Grade"
        ]

        csv_data = export.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇️ Download CSV",
            data=csv_data,
            file_name="student_performance.csv",
            mime="text/csv",
            type="primary"
        )

        st.caption("CSV contains all student information, marks, totals, percentage, grade and rank.")