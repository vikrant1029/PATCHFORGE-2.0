import streamlit as st
import requests
from datetime import datetime


# ============================================================
# PATCHFORGE 2.0 | TEAM KRYNEXA
# PREMIUM INTERACTIVE MISSION CONTROL
# BUILD. EVOLVE. PROTECT.
# ============================================================

st.set_page_config(
    page_title="PATCHFORGE 2.0 | Mission Control",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

DEFAULT_API = "http://127.0.0.1:8002"


# ============================================================
# 1. MODULE DIRECTORY
# ============================================================

MODULES = [
    {
        "id": "01",
        "name": "Health Monitoring",
        "icon": "🩺",
        "keyword": "health",
        "description": "Live backend availability monitoring.",
        "purpose": "Checks backend connectivity.",
        "endpoint": "/api/v1/health",
        "page": "Health Monitoring"
    },
    {
        "id": "02",
        "name": "AI Orchestrator",
        "icon": "🧠",
        "keyword": "orchestrator",
        "description": "Engineering workflow coordinator.",
        "purpose": "Executes engineering missions.",
        "endpoint": "/api/v1/orchestrator/execute",
        "page": "Autonomous Mission"
    },
    {
        "id": "03",
        "name": "Repository Intelligence",
        "icon": "📁",
        "keyword": "repository",
        "description": "Repository inspection and source discovery.",
        "purpose": "Scans repository structure.",
        "endpoint": "/api/v1/repository/scan",
        "page": "Repository Intelligence"
    },
    {
        "id": "04",
        "name": "Bug Detection Engine",
        "icon": "🐛",
        "keyword": "bugs",
        "description": "Automated source code bug detection.",
        "purpose": "Detects suspicious code patterns.",
        "endpoint": "/api/v1/bugs/scan",
        "page": "Bug Detection"
    },
    {
        "id": "05",
        "name": "Code Quality Analyzer",
        "icon": "📊",
        "keyword": "quality",
        "description": "Static code quality analysis.",
        "purpose": "Analyzes code quality.",
        "endpoint": "/api/v1/quality/analyze",
        "page": "Code Quality"
    },
    {
        "id": "06",
        "name": "AI Code Improver",
        "icon": "⚡",
        "keyword": "improver",
        "description": "Safe code improvement and fixing.",
        "purpose": "Previews and applies approved safe fixes.",
        "endpoint": "/api/v1/improver/preview",
        "page": "AI Improver"
    },
    {
        "id": "07",
        "name": "Database Intelligence",
        "icon": "🗄️",
        "keyword": "database",
        "description": "Persistent mission storage and analytics.",
        "purpose": "Stores and retrieves mission records.",
        "endpoint": "/api/v1/database/overview",
        "page": "Database Intelligence"
    }
]


# ============================================================
# 2. SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "navigation": "Overview",
    "api_url": DEFAULT_API,
    "health_result": None,
    "last_quality": None,
    "last_bug": None,
    "last_repository": None,
    "last_mission": None,
    "last_improvement": None,
    "safe_fix_preview": None,
    "safe_fix_preview_path": None,
    "safe_fix_apply": None,
    "safe_fix_restore": None,
    "improver_status": None,
    "task_detail": None,
    "database_detail": None,
    "last_refresh": None
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# 3. NAVIGATION CALLBACK
# ============================================================

PAGES = [
    "Overview",
    "Health Monitoring",
    "Autonomous Mission",
    "Task History",
    "Database Intelligence",
    "Module Guide",
    "Repository Intelligence",
    "Bug Detection",
    "Code Quality",
    "AI Improver",
    "System Intelligence"
]


def navigate_to(page_name):
    """Update navigation before Streamlit creates the radio widget."""
    st.session_state.navigation = page_name


# ============================================================
# 4. PREMIUM CSS
# ============================================================

st.markdown("""
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
);

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 5%, #17244a 0%, transparent 30%),
        radial-gradient(circle at 90% 90%, #151b43 0%, transparent 30%),
        #070b14;
    color: #eaf2ff;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#0c1527,#080e1b);
    border-right: 1px solid rgba(76,130,200,.22);
}

[data-testid="stSidebar"] * {
    color: #dceaff;
}

.block-container {
    max-width: 1550px;
    padding-top: 1.6rem;
}

.hero {
    padding: 34px;
    border-radius: 22px;
    border: 1px solid rgba(90,165,255,.35);
    background: linear-gradient(110deg,#0f2342,#181943,#0a2a3d);
    box-shadow: 0 15px 50px rgba(0,0,0,.25);
    margin-bottom: 25px;
}

.hero h1 {
    color: white;
    font-size: 39px;
    font-weight: 800;
}

.hero h3 {
    color: #a7c8f5;
    font-size: 17px;
}

.hero p {
    color: #65c9ff;
    letter-spacing: 3px;
    font-size: 11px;
    font-weight: 700;
}

.hero-tag {
    display: inline-block;
    padding: 7px 13px;
    border-radius: 30px;
    background: rgba(30,144,255,.12);
    border: 1px solid rgba(75,170,255,.35);
    color: #83caff;
    font-size: 11px;
    font-weight: 700;
}

.module-card {
    min-height: 205px;
    padding: 22px;
    margin-bottom: 12px;
    border-radius: 17px;
    background: linear-gradient(145deg,#15253f,#0a1222);
    border: 1px solid rgba(91,145,205,.25);
    box-shadow: 0 12px 30px rgba(0,0,0,.2);
}

.module-number {
    color: #6db8ff;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 3px;
}

.module-icon {
    font-size: 31px;
    margin: 15px 0 12px;
}

.module-name {
    color: #f2f7ff;
    font-size: 16px;
    font-weight: 750;
}

.module-description {
    color: #91a8c5;
    font-size: 11px;
    line-height: 1.6;
    margin-top: 8px;
}

.module-status {
    font-size: 9px;
    letter-spacing: 1.5px;
    margin-top: 14px;
    font-weight: 800;
}

.info-card {
    padding: 18px;
    border-radius: 13px;
    background: linear-gradient(145deg,#14233b,#0e192b);
    border: 1px solid #294363;
    margin-bottom: 12px;
    min-height: 100px;
}

.info-title {
    color: #74c7ff;
    font-size: 12px;
    font-weight: 800;
}

.info-text {
    color: #dceaff;
    font-size: 13px;
    margin-top: 7px;
    line-height: 1.6;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg,#14233b,#0e192b);
    border: 1px solid #294363;
    border-radius: 13px;
    padding: 17px;
}

[data-testid="stMetricLabel"] {
    color: #94b2d5;
}

[data-testid="stMetricValue"] {
    color: white;
    font-weight: 800;
}

div.stButton > button {
    background: linear-gradient(100deg,#1767d1,#663de0);
    color: white;
    border: 1px solid rgba(120,170,255,.3);
    border-radius: 10px;
    min-height: 43px;
    font-weight: 700;
}

div.stButton > button:hover {
    border-color: #65caff;
    box-shadow: 0 0 18px rgba(40,150,255,.3);
}

div[data-testid="stExpander"] {
    background: rgba(17,30,50,.8);
    border: 1px solid #263d5d;
    border-radius: 12px;
}

.footer {
    text-align: center;
    color: #7792b7;
    padding: 22px;
    border-top: 1px solid #1d3049;
    margin-top: 30px;
}

.footer strong {
    color: #75bfff;
    letter-spacing: 2px;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 5. API ENGINE
# ============================================================

def api_request(method, endpoint, payload=None, timeout=60):

    url = st.session_state.api_url.rstrip("/") + endpoint

    try:

        response = requests.request(
            method=method,
            url=url,
            json=payload,
            timeout=timeout
        )

        try:
            data = response.json()
        except ValueError:
            data = {"response_text": response.text}

        if not isinstance(data, dict):
            data = {"data": data}

        data["_http_ok"] = response.ok
        data["_http_status"] = response.status_code

        if not response.ok:
            data.setdefault(
                "error",
                data.get("detail", response.reason)
            )

        return data

    except requests.RequestException as error:

        return {
            "success": False,
            "_http_ok": False,
            "error": str(error)
        }


def api_get(endpoint, timeout=60):
    return api_request("GET", endpoint, timeout=timeout)


def api_post(endpoint, payload=None, timeout=120):
    return api_request(
        "POST",
        endpoint,
        payload=payload,
        timeout=timeout
    )


def request_ok(result):

    return (
        isinstance(result, dict)
        and result.get("_http_ok", False)
        and result.get("success") is not False
    )


def get_api_schema():

    result = api_get("/openapi.json")

    if not result.get("_http_ok"):
        return None

    return result if "paths" in result else None


def module_registered(schema, keyword):

    if not schema:
        return False

    return any(
        keyword in path.lower()
        for path in schema.get("paths", {})
    )


def endpoint_method(schema, endpoint):

    if not schema:
        return None

    methods = schema.get("paths", {}).get(endpoint, {})

    for method in ["get", "post"]:
        if method in methods:
            return method.upper()

    return None


def execute_scan(endpoint, schema):

    method = endpoint_method(schema, endpoint)

    if method is None:
        return {
            "success": False,
            "error": f"Endpoint unavailable: {endpoint}"
        }

    if method == "GET":
        return api_get(endpoint)

    return api_post(endpoint, {})


def show_result(result):

    if request_ok(result):
        st.success("API REQUEST SUCCESSFUL")
    else:
        st.error(result.get("error", "API request failed."))

    st.json(result)


def get_data(result):

    if not isinstance(result, dict):
        return {}

    data = result.get("data", result)

    return data if isinstance(data, dict) else {}


def show_module_details(module):

    a, b = st.columns(2)

    with a:

        st.markdown(f"""
        <div class="info-card">
            <div class="info-title">PURPOSE</div>
            <div class="info-text">{module["purpose"]}</div>
        </div>
        """, unsafe_allow_html=True)

    with b:

        st.markdown(f"""
        <div class="info-card">
            <div class="info-title">API ENDPOINT</div>
            <div class="info-text">{module["endpoint"]}</div>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# 6. HEADER
# ============================================================

st.markdown("""
<div class="hero">
    <div class="hero-tag">AUTONOMOUS ENGINEERING PLATFORM</div>
    <h1>⚡ PATCHFORGE 2.0</h1>
    <h3>Intelligent Software Engineering. One Mission Control.</h3>
    <p>TEAM KRYNEXA | BUILD. EVOLVE. PROTECT.</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# 7. SIDEBAR
# ============================================================

st.sidebar.markdown("## ⚡ PATCHFORGE")
st.sidebar.caption("MISSION CONTROL / NODE ALPHA")
st.sidebar.divider()

page = st.sidebar.radio(
    "COMMAND NAVIGATION",
    PAGES,
    key="navigation"
)

st.sidebar.divider()

st.sidebar.markdown("### ◈ CONNECTION SETTINGS")

st.session_state.api_url = st.sidebar.text_input(
    "Backend API URL",
    value=st.session_state.api_url,
    key="backend_url_input"
).rstrip("/")

st.sidebar.caption("FastAPI backend connection")

if st.sidebar.button(
    "🔄 REFRESH DASHBOARD",
    use_container_width=True
):
    st.rerun()

st.sidebar.divider()

st.sidebar.markdown("### ◈ PLATFORM IDENTITY")
st.sidebar.markdown("**TEAM KRYNEXA**")
st.sidebar.caption("PATCHFORGE 2.0")
st.sidebar.caption("BUILD. EVOLVE. PROTECT.")


# ============================================================
# 8. BACKEND CONNECTION
# ============================================================

system_data = api_get(
    "/api/v1/system/status",
    timeout=15
)

is_online = request_ok(system_data)

schema = get_api_schema() if is_online else None

if st.session_state.last_refresh is None:

    st.session_state.last_refresh = datetime.now().strftime(
        "%d %b %Y | %I:%M:%S %p"
    )


# ============================================================
# 9. GLOBAL STATUS BAR
# ============================================================

st.markdown("### ◈ GLOBAL SYSTEM STATUS")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "BACKEND STATUS",
        "ONLINE" if is_online else "OFFLINE"
    )

with c2:
    st.metric("PLATFORM VERSION", "2.0.0")

with c3:

    registered_count = sum(
        1 for module in MODULES
        if module_registered(schema, module["keyword"])
    )

    st.metric(
        "REGISTERED MODULES",
        f"{registered_count}/07"
    )

with c4:

    st.metric(
        "SYSTEM STATE",
        "OPERATIONAL" if is_online else "DISCONNECTED"
    )

if is_online:
    st.success("● PATCHFORGE BACKEND CONNECTED")
else:
    st.error("● BACKEND CONNECTION FAILED")

st.divider()


# ============================================================
# 10. OVERVIEW
# ============================================================

if page == "Overview":

    st.markdown("## ◈ MISSION CONTROL CENTER")

    st.caption("Select any module to open its operational console.")

    cols = st.columns(3, gap="large")

    for index, module in enumerate(MODULES):

        registered = module_registered(
            schema,
            module["keyword"]
        )

        status_text = (
            "● API REGISTERED"
            if registered
            else "○ API NOT DETECTED"
        )

        status_color = (
            "#42dfa1" if registered else "#f5b85e"
        )

        with cols[index % 3]:

            st.markdown(f"""
            <div class="module-card">
                <div class="module-number">
                    MODULE / {module["id"]}
                </div>
                <div class="module-icon">{module["icon"]}</div>
                <div class="module-name">{module["name"]}</div>
                <div class="module-description">
                    {module["description"]}
                </div>
                <div class="module-status"
                     style="color:{status_color}">
                    {status_text}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.button(
                f"OPEN {module['name'].upper()}",
                key=f"open_module_{module['id']}",
                use_container_width=True,
                on_click=navigate_to,
                args=(module["page"],)
            )

    st.divider()

    st.markdown("### ◈ QUICK OPERATIONS")

    left, right = st.columns(2)

    with left:

        if st.button(
            "📊 RUN CODE QUALITY ANALYSIS",
            use_container_width=True
        ):

            with st.spinner("Analyzing repository..."):

                result = api_get("/api/v1/quality/analyze")

            st.session_state.last_quality = result

            show_result(result)

    with right:

        if st.button(
            "🩺 RUN LIVE HEALTH CHECK",
            use_container_width=True
        ):

            with st.spinner("Checking backend..."):

                result = api_get("/api/v1/health")

            st.session_state.health_result = result

            show_result(result)

    st.caption(
        f"Last refresh: {st.session_state.last_refresh}"
    )


# ============================================================
# 11. HEALTH MONITORING
# ============================================================

elif page == "Health Monitoring":

    st.markdown("## ◈ HEALTH MONITORING CENTER")

    st.write("Live backend health and connectivity monitoring.")

    if st.button(
        "🔄 RUN LIVE HEALTH CHECK",
        use_container_width=True
    ):

        with st.spinner("Checking backend health..."):

            st.session_state.health_result = api_get(
                "/api/v1/health",
                timeout=20
            )

    health = st.session_state.health_result

    if health is None:

        health = api_get("/api/v1/health", timeout=20)

        st.session_state.health_result = health

    if request_ok(health):

        st.success("BACKEND HEALTH API RESPONDING")

        a, b = st.columns(2)

        a.metric("BACKEND CONNECTION", "ONLINE")
        b.metric("HEALTH API", "RESPONDING")

    else:

        st.error("HEALTH CHECK FAILED")

        a, b = st.columns(2)

        a.metric("BACKEND CONNECTION", "FAILED")
        b.metric("HEALTH API", "UNAVAILABLE")

    st.markdown("### ◈ HEALTH API RESPONSE")
    st.json(health)

    st.markdown("### ◈ SYSTEM STATUS RESPONSE")
    st.json(system_data)


# ============================================================
# 12. AUTONOMOUS MISSION
# ============================================================

elif page == "Autonomous Mission":

    st.markdown("## ◈ AUTONOMOUS ENGINEERING MISSION")

    st.write(
        "Submit a software engineering task to PATCHFORGE Orchestrator."
    )

    st.info(
        "Mission execution uses the configured backend workflow. "
        "Code modification requires separate Safe Fix approval."
    )

    issue = st.text_area(
        "MISSION DESCRIPTION",
        placeholder=(
            "Analyze this repository, detect bugs and "
            "suggest improvements."
        ),
        height=140,
        max_chars=5000,
        key="mission_issue"
    )

    if st.button(
        "🚀 EXECUTE ENGINEERING MISSION",
        use_container_width=True
    ):

        if len(issue.strip()) < 5:

            st.warning("Enter a mission description.")

        elif not is_online:

            st.error("Backend is offline.")

        else:

            with st.spinner("Executing engineering mission..."):

                result = api_post(
                    "/api/v1/orchestrator/execute",
                    {"issue": issue.strip()}
                )

            st.session_state.last_mission = result

    result = st.session_state.last_mission

    if result:

        data = get_data(result)

        if request_ok(result):
            st.success("MISSION REQUEST COMPLETED")
        else:
            st.error(result.get("error", "Mission execution failed."))

        a, b, c = st.columns(3)

        a.metric(
            "TASK ID",
            str(data.get("task_id", "N/A"))
        )

        b.metric(
            "MISSION STATUS",
            str(data.get("status", "UNKNOWN"))
        )

        steps = data.get("steps", [])

        c.metric(
            "AGENT STEPS",
            len(steps) if isinstance(steps, list) else 0
        )

        if isinstance(steps, list) and steps:

            st.markdown("### ◈ AGENT EXECUTION STEPS")

            st.dataframe(
                steps,
                use_container_width=True,
                hide_index=True
            )

        st.markdown("### ◈ COMPLETE MISSION RESULT")
        st.json(result)


# ============================================================
# 13. TASK HISTORY
# ============================================================

elif page == "Task History":

    st.markdown("## ◈ ENGINEERING MISSION HISTORY")

    if st.button("🔄 REFRESH TASK HISTORY", use_container_width=True):
        st.rerun()

    history = api_get("/api/v1/orchestrator/tasks")

    if request_ok(history):

        tasks = history.get("tasks", [])

        if not isinstance(tasks, list):
            tasks = []

        st.metric(
            "TOTAL MISSIONS",
            history.get("total", len(tasks))
        )

        if tasks:

            st.dataframe(
                [
                    {
                        "Task ID": task.get("task_id", "N/A"),
                        "Status": task.get("status", "UNKNOWN"),
                        "Issue": task.get("issue", "N/A")
                    }
                    for task in tasks
                ],
                use_container_width=True,
                hide_index=True
            )

            task_ids = [
                str(task["task_id"])
                for task in tasks
                if task.get("task_id")
            ]

            if task_ids:

                selected_id = st.selectbox(
                    "SELECT TASK ID",
                    task_ids
                )

                if st.button("🔍 VIEW TASK REPORT"):

                    st.session_state.task_detail = api_get(
                        f"/api/v1/orchestrator/tasks/{selected_id}"
                    )

            if st.session_state.task_detail:

                st.markdown("### COMPLETE TASK REPORT")
                st.json(st.session_state.task_detail)

        else:

            st.info("No missions found.")

    else:

        st.error(
            history.get("error", "Unable to load task history.")
        )


# ============================================================
# 14. DATABASE INTELLIGENCE
# ============================================================

elif page == "Database Intelligence":

    st.markdown("## ◈ DATABASE INTELLIGENCE")

    if st.button(
        "🔄 REFRESH DATABASE INTELLIGENCE",
        use_container_width=True
    ):
        st.rerun()

    db_status = api_get("/api/v1/database/status")
    overview = api_get("/api/v1/database/overview")
    history = api_get("/api/v1/database/tasks")

    st.markdown("### ◈ DATABASE HEALTH")

    if request_ok(db_status):

        db = get_data(db_status)

        connected = db.get("connected", False)

        if connected:
            st.success("SQLITE DATABASE CONNECTED")
        else:
            st.warning("Database connection not confirmed.")

        a, b = st.columns(2)

        a.metric(
            "DATABASE ENGINE",
            db.get("database", "Unknown")
        )

        b.metric(
            "CONNECTION",
            "CONNECTED" if connected else "UNKNOWN"
        )

        st.code(str(db.get("path", "Unavailable")))

    else:

        st.error(
            db_status.get("error", "Database status unavailable.")
        )

    st.divider()

    st.markdown("### ◈ MISSION ANALYTICS")

    if request_ok(overview):

        stats = get_data(overview)

        total = stats.get("total_tasks", 0)
        completed = stats.get("completed_tasks", 0)
        failed = stats.get("failed_tasks", 0)
        running = stats.get("running_tasks", 0)
        pending = stats.get("pending_tasks", 0)

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("TOTAL", total)
        c2.metric("COMPLETED", completed)
        c3.metric("FAILED", failed)
        c4.metric("RUNNING", running)

        st.metric("PENDING", pending)

        if isinstance(total, (int, float)) and total > 0:

            rate = completed / total * 100

            st.progress(
                max(0.0, min(1.0, rate / 100))
            )

            st.caption(
                f"{rate:.1f}% missions completed."
            )

        with st.expander("VIEW COMPLETE DATABASE ANALYTICS"):
            st.json(overview)

    else:

        st.error(
            overview.get("error", "Database analytics unavailable.")
        )

    st.divider()

    st.markdown("### ◈ PERMANENT MISSION HISTORY")

    if request_ok(history):

        tasks = history.get("tasks", [])

        if not isinstance(tasks, list):
            tasks = []

        st.metric(
            "SAVED RECORDS",
            history.get("total", len(tasks))
        )

        if tasks:

            st.dataframe(
                [
                    {
                        "Task ID": task.get("task_id", "N/A"),
                        "Issue": task.get("issue", "N/A"),
                        "Status": task.get("status", "UNKNOWN"),
                        "Created": task.get("created_at", "N/A"),
                        "Updated": task.get("updated_at", "N/A")
                    }
                    for task in tasks
                ],
                use_container_width=True,
                hide_index=True
            )

            task_ids = [
                str(task["task_id"])
                for task in tasks
                if task.get("task_id")
            ]

            if task_ids:

                selected = st.selectbox(
                    "SELECT MISSION ID",
                    task_ids,
                    key="database_task_selector"
                )

                if st.button("🔍 VIEW COMPLETE MISSION REPORT"):

                    st.session_state.database_detail = api_get(
                        f"/api/v1/database/tasks/{selected}"
                    )

            if st.session_state.database_detail:
                st.json(st.session_state.database_detail)

        else:

            st.info("No saved missions found.")

    else:

        st.error(
            history.get("error", "Unable to retrieve database history.")
        )


# ============================================================
# 15. MODULE GUIDE
# ============================================================

elif page == "Module Guide":

    st.markdown("## ◈ PATCHFORGE MODULE GUIDE")

    for module in MODULES:

        registered = module_registered(
            schema,
            module["keyword"]
        )

        status = (
            "API REGISTERED"
            if registered
            else "API NOT DETECTED"
        )

        with st.expander(
            f'{module["id"]} | {module["icon"]} '
            f'{module["name"]} | {status}'
        ):

            st.write(module["description"])

            show_module_details(module)

            st.button(
                f"OPEN {module['name'].upper()}",
                key=f"guide_open_{module['id']}",
                on_click=navigate_to,
                args=(module["page"],)
            )


# ============================================================
# 16. REPOSITORY INTELLIGENCE
# ============================================================

elif page == "Repository Intelligence":

    module = MODULES[2]

    st.markdown("## ◈ REPOSITORY INTELLIGENCE")

    st.write(module["description"])

    show_module_details(module)

    if st.button(
        "📁 SCAN REPOSITORY",
        use_container_width=True
    ):

        with st.spinner("Scanning repository..."):

            result = execute_scan(
                "/api/v1/repository/scan",
                schema
            )

        st.session_state.last_repository = result

    if st.session_state.last_repository:

        st.markdown("### ◈ REPOSITORY SCAN RESULT")

        show_result(st.session_state.last_repository)


# ============================================================
# 17. BUG DETECTION
# ============================================================

elif page == "Bug Detection":

    module = MODULES[3]

    st.markdown("## ◈ BUG DETECTION ENGINE")

    st.write(module["description"])

    show_module_details(module)

    if st.button(
        "🐛 START BUG DETECTION",
        use_container_width=True
    ):

        with st.spinner("Running bug detection engine..."):

            result = execute_scan(
                "/api/v1/bugs/scan",
                schema
            )

        st.session_state.last_bug = result

    if st.session_state.last_bug:

        st.markdown("### ◈ BUG DETECTION REPORT")

        show_result(st.session_state.last_bug)


# ============================================================
# 18. CODE QUALITY
# ============================================================

elif page == "Code Quality":

    module = MODULES[4]

    st.markdown("## ◈ CODE QUALITY INTELLIGENCE")

    st.write(module["description"])

    show_module_details(module)

    if st.button(
        "⚡ ANALYZE CODE QUALITY",
        use_container_width=True
    ):

        with st.spinner("Analyzing codebase..."):

            result = api_get("/api/v1/quality/analyze")

        st.session_state.last_quality = result

    result = st.session_state.last_quality

    if result:

        if not request_ok(result):

            st.error(
                result.get("error", "Quality analysis failed.")
            )

            st.json(result)

        else:

            report = get_data(result)

            score = report.get("average_quality_score", 0)
            issues = report.get("total_issues", 0)
            files = report.get("analyzed_files", 0)

            try:
                score = float(score)
            except (ValueError, TypeError):
                score = 0

            score = max(0, min(100, score))

            a, b, c = st.columns(3)

            a.metric("QUALITY SCORE", f"{score:.1f}/100")
            b.metric("TOTAL ISSUES", issues)
            c.metric("FILES ANALYZED", files)

            st.progress(score / 100)

            if score >= 80:
                st.success("Strong quality score.")
            elif score >= 60:
                st.info("Moderate quality score.")
            else:
                st.warning("Several improvements may be required.")

            if report.get("files"):

                st.markdown("### ANALYZED FILES")

                st.dataframe(
                    report["files"],
                    use_container_width=True,
                    hide_index=True
                )

            if report.get("issues"):

                st.markdown("### DETECTED ISSUES")

                st.dataframe(
                    report["issues"],
                    use_container_width=True,
                    hide_index=True
                )

            with st.expander("VIEW COMPLETE JSON REPORT"):
                st.json(result)


# ============================================================
# 19. AI IMPROVER | SAFE FIX CENTER
# ============================================================

elif page == "AI Improver":

    st.markdown("## ◈ PATCHFORGE SAFE FIX CENTER")

    st.write(
        "Analyze code, preview safe fixes, approve modifications "
        "and restore original files from backups."
    )

    show_module_details(MODULES[5])

    st.divider()

    # ENGINE STATUS

    st.markdown("### ◈ IMPROVER ENGINE STATUS")

    if st.button("🔄 CHECK ENGINE STATUS", use_container_width=True):

        st.session_state.improver_status = api_get(
            "/api/v1/improver/status"
        )

    if st.session_state.improver_status is None:

        st.session_state.improver_status = api_get(
            "/api/v1/improver/status"
        )

    engine = st.session_state.improver_status

    if request_ok(engine):

        a, b, c = st.columns(3)

        a.metric(
            "ENGINE STATUS",
            engine.get("status", "UNKNOWN")
        )

        b.metric(
            "SAFE FIX TYPES",
            len(engine.get("safe_fix_types", []))
        )

        c.metric(
            "APPROVAL REQUIRED",
            "YES" if engine.get("approval_required") else "NO"
        )

        st.success("SAFE CODE IMPROVER CONNECTED")

        with st.expander("VIEW ENGINE INFORMATION"):
            st.json(engine)

    else:

        st.error(
            engine.get("error", "Improver engine unavailable.")
        )

    st.divider()

    # IMPROVEMENT ANALYSIS

    st.markdown("### ◈ AI IMPROVEMENT ANALYSIS")

    if st.button(
        "🚀 GENERATE IMPROVEMENT REPORT",
        use_container_width=True
    ):

        with st.spinner("Analyzing repository..."):

            result = api_post("/api/v1/improver/analyze")

        st.session_state.last_improvement = result

    result = st.session_state.last_improvement

    if result:

        if request_ok(result):

            st.success("Improvement report generated.")

            report = result.get("improvement_report", {})

            if not isinstance(report, dict):
                report = {}

            recommendations = report.get("recommendations", [])
            summary = report.get("severity_summary", {})

            if not isinstance(summary, dict):
                summary = {}

            a, b, c = st.columns(3)

            a.metric("HIGH PRIORITY", summary.get("HIGH", 0))
            b.metric("MEDIUM PRIORITY", summary.get("MEDIUM", 0))
            c.metric("LOW PRIORITY", summary.get("LOW", 0))

            st.metric(
                "FILES MODIFIED",
                report.get("files_modified", 0)
            )

            for index, item in enumerate(recommendations, 1):

                with st.expander(f"RECOMMENDATION {index}"):
                    st.json(item)

            with st.expander("VIEW COMPLETE IMPROVEMENT REPORT"):
                st.json(result)

        else:

            st.error(
                result.get("error", "Improvement analysis failed.")
            )

    st.divider()

    # SAFE FIX PREVIEW

    st.markdown("### ◈ SAFE FIX PREVIEW")

    st.info(
        "Preview changes before applying them. "
        "Preview does not modify the original source file."
    )

    file_path = st.text_input(
        "TARGET PYTHON FILE PATH",
        placeholder=r"C:\Project\example.py",
        key="safe_fix_file_path"
    )

    if st.button(
        "🔍 GENERATE SAFE FIX PREVIEW",
        use_container_width=True
    ):

        if not file_path.strip():

            st.warning("Enter a valid file path.")

        else:

            with st.spinner("Generating safe fix preview..."):

                preview_response = api_post(
                    "/api/v1/improver/preview",
                    {"file_path": file_path.strip()}
                )

            st.session_state.safe_fix_preview = preview_response
            st.session_state.safe_fix_preview_path = file_path.strip()
            st.session_state.safe_fix_apply = None

    preview = st.session_state.safe_fix_preview

    if preview:

        preview_data = preview.get("preview_result", {})

        if not isinstance(preview_data, dict):
            preview_data = {}

        if request_ok(preview) and preview_data.get("success"):

            st.success("SAFE FIX PREVIEW GENERATED")

            st.metric(
                "TOTAL CHANGES",
                preview_data.get("total_changes", 0)
            )

            changes = preview_data.get("changes", [])

            if changes:

                st.dataframe(
                    changes,
                    use_container_width=True,
                    hide_index=True
                )

            st.markdown("#### CODE DIFF")

            st.code(
                preview_data.get("diff", "No changes detected."),
                language="diff"
            )

            with st.expander("VIEW PROPOSED FIXED CODE"):

                st.code(
                    preview_data.get("preview", ""),
                    language="python"
                )

            st.caption(
                "Original file modified: "
                + str(preview_data.get("file_modified", False))
            )

        else:

            st.error(
                preview_data.get(
                    "error",
                    preview.get("error", "Preview failed.")
                )
            )

    st.divider()

    # APPLY FIX

    st.markdown("### ◈ APPROVAL & FIX EXECUTION")

    st.warning(
        "Applying a fix modifies the target file. "
        "Review the preview and ensure the backup is available."
    )

    approved = st.checkbox(
        "I have reviewed the preview and approve this code modification.",
        key="safe_fix_approval"
    )

    if st.button(
        "⚡ APPROVE & APPLY SAFE FIX",
        use_container_width=True
    ):

        saved_path = st.session_state.safe_fix_preview_path

        current_path = file_path.strip()

        preview_data = (
            preview.get("preview_result", {})
            if isinstance(preview, dict)
            else {}
        )

        if not preview:

            st.warning("Generate a preview before applying.")

        elif not saved_path or saved_path != current_path:

            st.warning("Generate a fresh preview for the current file path.")

        elif not approved:

            st.warning("Explicit approval is required.")

        elif not preview_data.get("success"):

            st.warning("A successful preview is required.")

        elif preview_data.get("total_changes", 0) == 0:

            st.info("No changes are available to apply.")

        else:

            with st.spinner("Applying approved safe fix..."):

                apply_response = api_post(
                    "/api/v1/improver/apply",
                    {
                        "file_path": saved_path,
                        "approved": True
                    }
                )

            st.session_state.safe_fix_apply = apply_response

            apply_data = apply_response.get("apply_result", {})

            if isinstance(apply_data, dict) and apply_data.get("backup"):

                st.session_state.restore_original_path = saved_path
                st.session_state.restore_backup_path = apply_data["backup"]

    applied = st.session_state.safe_fix_apply

    if applied:

        apply_data = applied.get("apply_result", {})

        if not isinstance(apply_data, dict):
            apply_data = {}

        if request_ok(applied) and apply_data.get("success"):

            st.success("SAFE FIX APPLIED SUCCESSFULLY")

            st.json(apply_data)

            if apply_data.get("backup"):

                st.markdown("### ◈ GENERATED BACKUP")

                st.code(apply_data["backup"])

        else:

            st.error(
                apply_data.get(
                    "error",
                    applied.get("error", "Fix application failed.")
                )
            )

    st.divider()

    # BACKUP RESTORE

    st.markdown("### ◈ BACKUP RESTORE CENTER")

    st.write("Restore a Python file from a previously generated backup.")

    restore_file = st.text_input(
        "ORIGINAL FILE PATH",
        key="restore_original_path"
    )

    backup_file = st.text_input(
        "BACKUP FILE PATH",
        key="restore_backup_path"
    )

    restore_approved = st.checkbox(
        "I approve restoring this backup.",
        key="restore_approval"
    )

    if st.button(
        "↩ RESTORE BACKUP",
        use_container_width=True
    ):

        if not restore_file.strip() or not backup_file.strip():

            st.warning("Enter both original and backup file paths.")

        elif not restore_approved:

            st.warning("Restore approval is required.")

        else:

            with st.spinner("Restoring backup..."):

                restore_response = api_post(
                    "/api/v1/improver/restore",
                    {
                        "file_path": restore_file.strip(),
                        "backup_path": backup_file.strip(),
                        "approved": True
                    }
                )

            st.session_state.safe_fix_restore = restore_response

    restored = st.session_state.safe_fix_restore

    if restored:

        restore_data = restored.get("restore_result", {})

        if not isinstance(restore_data, dict):
            restore_data = {}

        if request_ok(restored) and restore_data.get("success"):

            st.success("BACKUP RESTORED SUCCESSFULLY")

            st.json(restore_data)

        else:

            st.error(
                restore_data.get(
                    "error",
                    restored.get("error", "Backup restore failed.")
                )
            )

    st.divider()

    st.caption(
        "PATCHFORGE 2.0 | SAFE FIX CENTER | TEAM KRYNEXA"
    )


# ============================================================
# 20. SYSTEM INTELLIGENCE
# ============================================================

elif page == "System Intelligence":

    st.markdown("## ◈ SYSTEM INTELLIGENCE")

    if st.button("🔄 REFRESH SYSTEM", use_container_width=True):
        st.rerun()

    current_status = api_get("/api/v1/system/status")

    if request_ok(current_status):

        st.success("PATCHFORGE BACKEND ONLINE")

        st.markdown("### SYSTEM STATUS")
        st.json(current_status)

        info = api_get("/api/v1/system/info")

        if request_ok(info):

            st.markdown("### PLATFORM INFORMATION")
            st.json(info)

        else:

            st.warning(
                info.get("error", "System information unavailable.")
            )

        st.markdown("### REGISTERED API ENDPOINTS")

        if schema and "paths" in schema:

            for path, methods in schema["paths"].items():

                method_names = ", ".join(
                    method.upper()
                    for method in methods
                )

                with st.expander(f"{method_names}  {path}"):

                    for method, operation in methods.items():

                        st.write(
                            operation.get(
                                "summary",
                                "No description available"
                            )
                        )

                        if operation.get("description"):
                            st.caption(operation["description"])

        else:

            st.warning("OpenAPI schema unavailable.")

    else:

        st.error("Backend is offline. Start FastAPI server.")


# ============================================================
# 21. FOOTER
# ============================================================

st.markdown("""
<div class="footer">
    <h3>⚡ PATCHFORGE 2.0</h3>
    <strong>TEAM KRYNEXA</strong>
    <p>BUILD. EVOLVE. PROTECT.</p>
    <small>Autonomous AI Software Engineering Platform</small>
</div>
""", unsafe_allow_html=True)
