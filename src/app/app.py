 """PREDIX demonstration dashboard.

All risk signals in this interface are intentionally illustrative.  The only
portfolio figure presented as source data is the 1,775 ongoing projects
reported in PAIMANA's July 2026 report.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="PREDIX | Infrastructure Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Demo-only data. This deliberately does not imply project-level PAIMANA
# records or model output; it is only here to make the presentation interactive.
PROJECTS = [
    {
        "name": "Eastern Freight Corridor Upgrade",
        "code": "DEMO-TRN-1042",
        "sector": "Transport",
        "state": "Maharashtra",
        "agency": "National Transport Works Authority",
        "overall": "Critical",
        "cost_risk": "High",
        "schedule_risk": "Critical",
        "score": 91,
        "original_cost": 4_280,
        "revised_cost": 6_040,
        "expenditure": 2_710,
        "progress": 46,
        "approved": "Apr 2018",
        "original_completion": "Mar 2024",
        "revised_completion": "Dec 2027",
        "drivers": {
            "Schedule variance": (92, "High"),
            "Cost variance": (81, "High"),
            "Progress vs project age": (72, "Moderate"),
            "Expenditure pattern": (60, "Moderate"),
        },
        "warning": "Completion has moved materially beyond the original target while physical progress remains below the expected project stage.",
    },
    {
        "name": "Coastal Resilience & Water Grid",
        "code": "DEMO-WTR-0881",
        "sector": "Water",
        "state": "Tamil Nadu",
        "agency": "Coastal Water Development Board",
        "overall": "High",
        "cost_risk": "High",
        "schedule_risk": "High",
        "score": 82,
        "original_cost": 2_120,
        "revised_cost": 2_930,
        "expenditure": 1_180,
        "progress": 51,
        "approved": "Jan 2020",
        "original_completion": "Jun 2025",
        "revised_completion": "Mar 2027",
        "drivers": {
            "Schedule variance": (84, "High"),
            "Cost variance": (77, "High"),
            "Progress vs project age": (65, "Moderate"),
            "Expenditure pattern": (52, "Moderate"),
        },
        "warning": "Cost movement and revised schedule warrant a focused review of delivery constraints and remaining work packages.",
    },
    {
        "name": "Northern Grid Reliability Programme",
        "code": "DEMO-ENG-0614",
        "sector": "Energy",
        "state": "Rajasthan",
        "agency": "National Grid Modernisation Corporation",
        "overall": "High",
        "cost_risk": "Moderate",
        "schedule_risk": "High",
        "score": 76,
        "original_cost": 1_760,
        "revised_cost": 2_050,
        "expenditure": 1_315,
        "progress": 62,
        "approved": "Sep 2019",
        "original_completion": "Dec 2024",
        "revised_completion": "Sep 2026",
        "drivers": {
            "Schedule variance": (79, "High"),
            "Cost variance": (58, "Moderate"),
            "Progress vs project age": (66, "Moderate"),
            "Expenditure pattern": (47, "Low"),
        },
        "warning": "Schedule slippage is the dominant attention signal; check readiness of the remaining transmission packages.",
    },
    {
        "name": "Western Rail Capacity Expansion",
        "code": "DEMO-RLY-0398",
        "sector": "Railways",
        "state": "Gujarat",
        "agency": "Rail Infrastructure Delivery Unit",
        "overall": "High",
        "cost_risk": "High",
        "schedule_risk": "Moderate",
        "score": 71,
        "original_cost": 3_440,
        "revised_cost": 4_050,
        "expenditure": 2_980,
        "progress": 74,
        "approved": "May 2017",
        "original_completion": "Mar 2023",
        "revised_completion": "Jun 2026",
        "drivers": {
            "Schedule variance": (61, "Moderate"),
            "Cost variance": (73, "High"),
            "Progress vs project age": (56, "Moderate"),
            "Expenditure pattern": (49, "Low"),
        },
        "warning": "The revised cost is the primary monitor signal; inspect final-stage contract changes before closeout.",
    },
]

RISK_COLORS = {
    "Critical": "#f36b7f",
    "High": "#ffaf68",
    "Moderate": "#f6d77a",
    "Low": "#69d7ad",
}


def add_style() -> None:
    st.markdown(
        """
        <style>
        :root { --ink: #eaf2ff; --muted: #94a8c7; --line: rgba(164,191,231,.16);
                --panel: rgba(18,33,62,.78); --cyan: #49d9ff; --green: #69d7ad;
                --amber: #ffaf68; --red: #f36b7f; }
        .stApp { background: radial-gradient(circle at 84% -8%, #173a61 0, transparent 31%),
                           radial-gradient(circle at 0% 26%, #102c4a 0, transparent 26%), #071324; color: var(--ink); }
        [data-testid="stSidebar"] { background: linear-gradient(180deg,#0c1c33 0%,#081525 100%); border-right: 1px solid var(--line); }
        [data-testid="stSidebar"] * { color: var(--ink); }
        [data-testid="stSidebarNav"] { display: none; }
        .block-container { padding: 2.2rem 3rem 3.5rem; max-width: 1600px; }
        h1,h2,h3 { color: #f4f8ff !important; letter-spacing: -.025em; }
        h1 { font-size: 2.25rem !important; margin-bottom: .1rem !important; }
        h2 { font-size: 1.3rem !important; margin-top: 1.9rem !important; }
        h3 { font-size: .93rem !important; letter-spacing: .04em; text-transform: uppercase; }
        p, .stMarkdown, label { color: var(--muted); }
        .eyebrow { color: var(--cyan); font-weight: 700; letter-spacing: .13em; text-transform: uppercase; font-size: .72rem; }
        .brand { font-size: 1.7rem; font-weight: 800; letter-spacing: .13em; color: #fff; margin: 0; }
        .brand-mark { display:inline-grid; place-items:center; width:28px; height:28px; border:1px solid #49d9ff; color:#49d9ff; transform:rotate(45deg); margin-right:12px; font-size:.8rem; }
        .brand-mark span { transform:rotate(-45deg); }
        .subtitle { font-size: .92rem; color: var(--muted); margin-top: .4rem; }
        .demo-strip { display:flex; align-items:center; justify-content:space-between; gap:1rem; margin:1.7rem 0 1.4rem; padding:.72rem 1rem;
                      background:rgba(73,217,255,.075); border:1px solid rgba(73,217,255,.2); border-radius:10px; color:#bfeeff; font-size:.84rem; }
        .demo-badge { white-space:nowrap; color:#071324; background:#49d9ff; border-radius:99px; font-size:.68rem; font-weight:800; letter-spacing:.1em; padding:.28rem .58rem; }
        div[data-testid="stMetric"] { background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:1.05rem 1.1rem; min-height:126px; }
        div[data-testid="stMetricLabel"] { color:var(--muted); font-size:.7rem; letter-spacing:.08em; text-transform:uppercase; }
        div[data-testid="stMetricValue"] { color:#f7fbff; font-size:1.78rem; }
        div[data-testid="stMetricDelta"] { font-size:.72rem; }
        .section-note { color:var(--muted); font-size:.82rem; margin-top:-.45rem; margin-bottom:.8rem; }
        .risk-pill { display:inline-block; font-size:.69rem; font-weight:800; letter-spacing:.07em; padding:.22rem .54rem; border-radius:99px; }
        .pill-critical { color:#ffd7dd; background:rgba(243,107,127,.18); }
        .pill-high { color:#ffe0bd; background:rgba(255,175,104,.18); }
        .pill-moderate { color:#ffedb2; background:rgba(246,215,122,.16); }
        .pill-low { color:#c7f7e4; background:rgba(105,215,173,.16); }
        .project-card { background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:1.1rem 1.2rem; margin-bottom:.65rem; }
        .project-title { color:#f5f8ff; font-size:1rem; font-weight:650; margin-bottom:.3rem; }
        .project-meta { color:var(--muted); font-size:.78rem; }
        .signal { margin:.4rem 0 .75rem; padding:.7rem .85rem; border-left:3px solid var(--amber); background:rgba(255,175,104,.08); color:#ffdcb6; border-radius:0 8px 8px 0; font-size:.86rem; }
        .detail-hero { padding:1.5rem 1.6rem; border-radius:16px; background:linear-gradient(125deg,rgba(28,51,87,.9),rgba(18,33,62,.8)); border:1px solid rgba(73,217,255,.25); }
        .risk-score { color:#f7fbff; font-size:3.5rem; font-weight:800; line-height:1; }
        .caption { color:var(--muted); font-size:.76rem; }
        .info-grid { display:grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap:0; border:1px solid var(--line); border-radius:12px; overflow:hidden; }
        .info-item { padding:.78rem .9rem; border-bottom:1px solid var(--line); }
        .info-item:nth-child(odd) { border-right:1px solid var(--line); }
        .info-label { display:block; color:var(--muted); font-size:.68rem; letter-spacing:.08em; text-transform:uppercase; }
        .info-value { display:block; color:#f2f6ff; font-size:.9rem; margin-top:.18rem; }
        .driver-row { display:grid; grid-template-columns: 170px 1fr 70px; align-items:center; gap:.8rem; margin:.85rem 0; color:#e9f1ff; font-size:.88rem; }
        .driver-track { height:8px; overflow:hidden; border-radius:99px; background:rgba(151,175,212,.15); }
        .driver-fill { height:100%; border-radius:99px; background:linear-gradient(90deg,#49d9ff,#ffaf68); }
        .driver-value { text-align:right; font-size:.72rem; font-weight:700; color:#ffcf9f; }
        .alert-card { background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:1.05rem 1.15rem; margin-bottom:.75rem; }
        .alert-head { display:flex; justify-content:space-between; align-items:center; gap:.6rem; }
        .alert-name { color:#f6f9ff; font-size:.98rem; font-weight:650; }
        .alert-reason { color:var(--muted); font-size:.85rem; margin:.55rem 0 .85rem; }
        .sidebar-foot { position:fixed; bottom:1.25rem; left:1rem; right:1rem; color:#627796; font-size:.72rem; }
        .stButton > button { border:1px solid rgba(73,217,255,.32); background:rgba(73,217,255,.09); color:#d9f7ff; border-radius:8px; font-weight:600; }
        .stButton > button:hover { border-color:#49d9ff; color:#fff; }
        [data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
        @media(max-width: 800px) { .block-container { padding:1.35rem 1rem 2.4rem; } .driver-row{grid-template-columns: 120px 1fr 58px; gap:.5rem;} .info-grid{grid-template-columns:1fr;} .info-item:nth-child(odd){border-right:0;} }
        </style>
        """,
        unsafe_allow_html=True,
    )


def pill(risk: str) -> str:
    return f'<span class="risk-pill pill-{risk.lower()}">{risk.upper()}</span>'


def demo_strip() -> None:
    st.markdown(
        """
        <div class="demo-strip">
            <span><b>Prototype / illustrative.</b> Risk scores, project entries and portfolio splits demonstrate the intended workflow; they are not model outputs.</span>
            <span class="demo-badge">DEMO MODE</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(f'<div class="eyebrow">{eyebrow}</div><h1>{title}</h1><div class="subtitle">{subtitle}</div>', unsafe_allow_html=True)


def select_project(label: str = "Inspect a demo project") -> dict:
    names = [project["name"] for project in PROJECTS]
    current = st.session_state.get("selected_project", names[0])
    index = names.index(current) if current in names else 0
    selected = st.selectbox(label, names, index=index, label_visibility="visible")
    st.session_state.selected_project = selected
    return next(project for project in PROJECTS if project["name"] == selected)


def portfolio_page() -> None:
    page_header("Portfolio intelligence", "Monitor what deserves attention first.", "A focused decision view for a large infrastructure portfolio.")
    demo_strip()

    metrics = st.columns(4)
    metrics[0].metric("Total ongoing projects", "1,775", "PAIMANA · July 2026")
    metrics[1].metric("Critical risk", "46", "Illustrative demo count", delta_color="off")
    metrics[2].metric("High risk", "128", "Illustrative demo count", delta_color="off")
    metrics[3].metric("Average progress", "63%", "Illustrative demo metric", delta_color="off")

    st.markdown("## Demo risk distribution")
    st.markdown('<div class="section-note">A presentation scenario, not a PREDIX prediction. Select a segment to see its narrative.</div>', unsafe_allow_html=True)
    risk_dist = pd.DataFrame(
        {"Risk level": ["Critical", "High", "Moderate", "Low"], "Share of demo portfolio": [8, 16, 29, 47]}
    )
    fig = px.bar(
        risk_dist,
        x="Share of demo portfolio",
        y="Risk level",
        orientation="h",
        text="Share of demo portfolio",
        color="Risk level",
        color_discrete_map=RISK_COLORS,
    )
    fig.update_traces(texttemplate="%{x}%", textposition="outside", hovertemplate="%{y}: %{x}% of demo portfolio<extra></extra>")
    fig.update_layout(
        height=255,
        showlegend=False,
        margin=dict(l=0, r=45, t=4, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dce8fb"),
        xaxis=dict(showgrid=True, gridcolor="rgba(164,191,231,.12)", title="Share of demo portfolio (%)", range=[0, 55]),
        yaxis=dict(categoryorder="array", categoryarray=["Critical", "High", "Moderate", "Low"], title=""),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("## Projects requiring attention")
    st.markdown('<div class="section-note">Start with a manageable priority list — not 1,775 manual inspections.</div>', unsafe_allow_html=True)
    rows = []
    for project in PROJECTS:
        rows.append(
            {
                "Project": project["name"],
                "Sector": project["sector"],
                "Cost risk": project["cost_risk"],
                "Schedule risk": project["schedule_risk"],
                "Overall risk": project["overall"],
                "Demo score": project["score"],
            }
        )
    table = pd.DataFrame(rows)
    st.dataframe(
        table,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Demo score": st.column_config.ProgressColumn("Demo score", min_value=0, max_value=100, format="%d / 100"),
        },
    )
    selected = select_project()
    open_col, context_col = st.columns([1, 3])
    if open_col.button("Open project profile →", use_container_width=True):
        st.session_state.page = "Project detail"
        st.rerun()
    context_col.markdown(f'<div class="signal"><b>{selected["name"]}</b> is selected. Its score and drivers are illustrative demo values.</div>', unsafe_allow_html=True)


def project_page() -> None:
    page_header("Project detail", "Investigate one project, with context.", "Evidence, risk signals and recommended focus areas in one presentation view.")
    demo_strip()
    project = select_project("Selected project")
    risk_color = RISK_COLORS[project["overall"]]

    hero, overview = st.columns([1, 2], gap="large")
    with hero:
        st.markdown(
            f'''<div class="detail-hero">
                <div class="eyebrow">Overall demo risk</div>
                <div style="margin:.75rem 0">{pill(project["overall"])}</div>
                <div class="risk-score" style="color:{risk_color}">{project["score"]}<span style="font-size:1.25rem;color:#94a8c7">/100</span></div>
                <div class="caption" style="margin-top:.55rem">Illustrative risk score · not a model result</div>
            </div>''',
            unsafe_allow_html=True,
        )
    with overview:
        st.markdown("### Risk overview")
        cost, schedule, progress = st.columns(3)
        cost.metric("Cost risk", project["cost_risk"], "Illustrative")
        schedule.metric("Schedule risk", project["schedule_risk"], "Illustrative")
        progress.metric("Physical progress", f'{project["progress"]}%', "Demo profile")

    st.markdown("## Project profile")
    st.markdown('<div class="section-note">The fields mirror the kind of information available in PAIMANA’s ongoing-project table. Values below are demo content.</div>', unsafe_allow_html=True)
    profile_html = f'''<div class="info-grid">
        <div class="info-item"><span class="info-label">Project name</span><span class="info-value">{project["name"]}</span></div>
        <div class="info-item"><span class="info-label">Project code</span><span class="info-value">{project["code"]}</span></div>
        <div class="info-item"><span class="info-label">Implementing agency</span><span class="info-value">{project["agency"]}</span></div>
        <div class="info-item"><span class="info-label">Sector · state</span><span class="info-value">{project["sector"]} · {project["state"]}</span></div>
        <div class="info-item"><span class="info-label">Original cost</span><span class="info-value">₹{project["original_cost"]:,} Cr</span></div>
        <div class="info-item"><span class="info-label">Revised cost</span><span class="info-value">₹{project["revised_cost"]:,} Cr</span></div>
        <div class="info-item"><span class="info-label">Original completion</span><span class="info-value">{project["original_completion"]}</span></div>
        <div class="info-item"><span class="info-label">Revised completion</span><span class="info-value">{project["revised_completion"]}</span></div>
        <div class="info-item"><span class="info-label">Cumulative expenditure</span><span class="info-value">₹{project["expenditure"]:,} Cr</span></div>
        <div class="info-item"><span class="info-label">Physical progress</span><span class="info-value">{project["progress"]}%</span></div>
    </div>'''
    st.markdown(profile_html, unsafe_allow_html=True)

    left, right = st.columns([1.05, .95], gap="large")
    with left:
        st.markdown("## Why this project needs attention")
        st.markdown('<div class="section-note">Explainable demo signals — designed to guide review, not replace it.</div>', unsafe_allow_html=True)
        drivers = ""
        for driver, (strength, label) in project["drivers"].items():
            drivers += f'''<div class="driver-row"><span>{driver}</span><div class="driver-track"><div class="driver-fill" style="width:{strength}%"></div></div><span class="driver-value">{label.upper()}</span></div>'''
        st.markdown(f'<div class="project-card">{drivers}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="signal"><b>Early warning</b><br>{project["warning"]}</div>', unsafe_allow_html=True)
    with right:
        st.markdown("## Schedule movement")
        st.markdown('<div class="section-note">The original and revised dates keep the delay narrative tangible.</div>', unsafe_allow_html=True)
        timeline = go.Figure()
        timeline.add_trace(go.Scatter(
            x=[pd.to_datetime("2018-01-01"), pd.to_datetime("2028-01-01")], y=[1, 1],
            mode="lines", line=dict(color="rgba(164,191,231,.25)", width=5), hoverinfo="skip", showlegend=False,
        ))
        for label, value, marker_color, y in [
            ("Original completion", project["original_completion"], "#69d7ad", 1),
            ("Revised completion", project["revised_completion"], "#f36b7f", 1),
        ]:
            parsed = pd.to_datetime(value)
            timeline.add_trace(go.Scatter(
                x=[parsed], y=[y], mode="markers+text", text=[label + "<br>" + value], textposition="top center",
                marker=dict(size=16, color=marker_color, line=dict(color="#081525", width=2)), name=label,
                hovertemplate=f"{label}: {value}<extra></extra>",
            ))
        timeline.update_layout(
            height=255, margin=dict(l=0, r=0, t=35, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#dce8fb"), showlegend=False,
            xaxis=dict(title="Target completion", gridcolor="rgba(164,191,231,.12)", dtick="M12", tickformat="%Y"),
            yaxis=dict(visible=False, range=[.83, 1.22]),
        )
        st.plotly_chart(timeline, use_container_width=True, config={"displayModeBar": False})


def analytics_page() -> None:
    page_header("Portfolio analytics", "See where attention clusters.", "Illustrative drill-downs for the portfolio-intelligence story.")
    demo_strip()
    st.markdown("## Demo concentration of elevated risk")
    st.markdown('<div class="section-note">These charts use prototype scenario values, not calculated PREDIX results.</div>', unsafe_allow_html=True)
    analytics = [
        ("Risk by sector", pd.DataFrame({"Group": ["Transport", "Railways", "Energy", "Water"], "Elevated-risk share": [42, 35, 29, 18]})),
        ("Risk by state", pd.DataFrame({"Group": ["Maharashtra", "Tamil Nadu", "Rajasthan", "Gujarat"], "Elevated-risk share": [39, 31, 27, 22]})),
        ("Risk by agency", pd.DataFrame({"Group": ["Transport Works", "Grid Modernisation", "Water Development", "Rail Delivery"], "Elevated-risk share": [41, 34, 25, 21]})),
    ]
    cols = st.columns(3)
    for col, (title, frame) in zip(cols, analytics):
        with col:
            fig = px.bar(frame, x="Elevated-risk share", y="Group", orientation="h", text="Elevated-risk share")
            fig.update_traces(marker_color="#49d9ff", texttemplate="%{x}%", textposition="outside", hovertemplate="%{y}: %{x}%<extra></extra>")
            fig.update_layout(
                title=dict(text=title, font=dict(size=15, color="#f4f8ff")), height=310, margin=dict(l=0, r=30, t=45, b=5),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#dce8fb"),
                xaxis=dict(range=[0, 52], gridcolor="rgba(164,191,231,.12)", title="Share (%)"), yaxis=dict(title="", autorange="reversed"),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("## Presentation cue")
    st.markdown('<div class="signal"><b>From individual projects to portfolio intelligence.</b><br>Use this page to explain that PREDIX can help leaders spot concentration areas before they decide where to investigate.</div>', unsafe_allow_html=True)


def warnings_page() -> None:
    page_header("Early warning center", "Turn signals into a review queue.", "A practical handoff from monitoring to intervention.")
    demo_strip()
    st.markdown("## Priority signals")
    st.markdown('<div class="section-note">Each alert is a demo narrative based on the illustrative project profiles.</div>', unsafe_allow_html=True)
    for project in PROJECTS[:3]:
        reason = project["warning"]
        st.markdown(
            f'''<div class="alert-card"><div class="alert-head"><div><div class="alert-name">{project["name"]}</div>
            <div class="project-meta">{project["sector"]} · {project["state"]} · {project["code"]}</div></div>{pill(project["overall"])}</div>
            <div class="alert-reason"><b>Review prompt:</b> {reason}</div></div>''',
            unsafe_allow_html=True,
        )
        key = "warning-" + project["code"]
        if st.button(f'View {project["code"]} →', key=key):
            st.session_state.selected_project = project["name"]
            st.session_state.page = "Project detail"
            st.rerun()


def sidebar() -> str:
    with st.sidebar:
        st.markdown('<div class="brand"><span class="brand-mark"><span>◈</span></span>PREDIX</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle" style="margin: .8rem 0 2rem">Predictive Infrastructure Monitoring &amp; Early Warning System</div>', unsafe_allow_html=True)
        choices = ["Portfolio", "Project detail", "Analytics", "Early warning"]
        current = st.session_state.get("page", "Portfolio")
        if current not in choices:
            current = "Portfolio"
        page = st.radio("Navigate", choices, index=choices.index(current), label_visibility="collapsed")
        st.session_state.page = page
        st.markdown('<div class="sidebar-foot">PREDIX prototype<br>SIH 2026 · decision-support concept</div>', unsafe_allow_html=True)
    return page


def main() -> None:
    add_style()
    page = sidebar()
    if page == "Portfolio":
        portfolio_page()
    elif page == "Project detail":
        project_page()
    elif page == "Analytics":
        analytics_page()
    else:
        warnings_page()


if __name__ == "__main__":
    main()
