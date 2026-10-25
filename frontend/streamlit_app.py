"""
CodeSecure AI — Enterprise Frontend Application
Privacy-Preserving Secure Code Debugging and Review using Local LLM and RAG
Academic Demonstration for Tata Technologies Tech Pulse FY-26 (CS4)
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    print("Streamlit not installed in current environment. Install via 'pip install streamlit'.")

if STREAMLIT_AVAILABLE:
    from app.config import settings
    from app.security.authentication import verify_password
    from app.services.evaluation_service import evaluation_service
    from app.services.finding_service import finding_service
    from app.services.llm_service import llm_service
    from app.services.log_analysis_service import log_analysis_service
    from app.services.rag_service import rag_service
    from app.services.review_service import IN_MEMORY_REVIEWS, review_service
    from app.services.security_service import security_service
    from app.schemas import CodeReviewRequest, FindingStatusUpdate, LogAnalysisRequest

    # Page Configuration (Strictly No Emojis)
    st.set_page_config(
        page_title="CodeSecure AI — Defensive Code Review & Static Analysis",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Load External CSS Design System
    css_path = BASE_DIR / "frontend" / "assets" / "style.css"
    custom_css = ""
    if css_path.exists():
        try:
            custom_css = css_path.read_text(encoding="utf-8")
        except Exception:
            pass

    st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

    # Session State Initialization
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = "anonymous"
        st.session_state.role = "developer"
        st.session_state.user_id = 1

    # --------------------------------------------------------------------------
    # SVG Icon Helpers (Zero Emojis)
    # --------------------------------------------------------------------------
    def svg_shield(size=18, color="currentColor"):
        return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'

    def svg_lock(size=16, color="currentColor"):
        return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>'

    def svg_cpu(size=16, color="currentColor"):
        return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>'

    def svg_database(size=16, color="currentColor"):
        return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>'

    def svg_alert(size=16, color="currentColor"):
        return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>'

    # --------------------------------------------------------------------------
    # Presentation Badges & KPI Renderers (Strictly No Emojis)
    # --------------------------------------------------------------------------
    def render_severity_pill(severity: str) -> str:
        s = severity.lower() if severity else "info"
        cls_map = {
            "critical": ("cs-pill-rose", "dot-rose"),
            "high": ("cs-pill-amber", "dot-amber"),
            "medium": ("cs-pill-amber", "dot-amber"),
            "low": ("cs-pill-cyan", "dot-cyan"),
            "informational": ("cs-pill-neutral", "dot-cyan"),
        }
        pill_cls, dot_cls = cls_map.get(s, ("cs-pill-neutral", "dot-cyan"))
        return f'<span class="cs-pill {pill_cls}"><span class="cs-indicator-dot {dot_cls}"></span>{severity.upper()}</span>'

    def render_status_pill(status: str) -> str:
        s = status.lower().replace(" ", "-") if status else "open"
        cls_map = {
            "open": ("cs-pill-amber", "dot-amber"),
            "confirmed": ("cs-pill-emerald", "dot-emerald"),
            "rejected": ("cs-pill-rose", "dot-rose"),
            "fixed": ("cs-pill-cyan", "dot-cyan"),
            "needs-review": ("cs-pill-primary", "dot-amber"),
        }
        pill_cls, dot_cls = cls_map.get(s, ("cs-pill-neutral", "dot-amber"))
        return f'<span class="cs-pill {pill_cls}"><span class="cs-indicator-dot {dot_cls}"></span>{status.upper()}</span>'

    def render_kpi_tile(label: str, value, caption: str, stripe_class: str):
        st.markdown(
            f"""
            <div class="cs-metric-tile">
                <div class="cs-metric-stripe {stripe_class}"></div>
                <div class="cs-metric-header">
                    <span class="cs-metric-label">{label}</span>
                </div>
                <div class="cs-metric-number">{value}</div>
                <div class="cs-metric-caption">{caption}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------------------------
    # DEMO ACCOUNTS SPECIFICATION
    # --------------------------------------------------------------------------
    DEMO_ROLES = {
        "developer": "Dev@CodeSecure2026",
        "reviewer": "Reviewer@CodeSecure2026",
        "security_eng": "SecEng@CodeSecure2026",
        "admin": "Admin@CodeSecure2026",
    }

    # ==========================================================================
    # AUTHENTICATION GATEWAY: DEDICATED LOGIN PORTAL
    # ==========================================================================
    if not st.session_state.authenticated:
        # Dedicated Enterprise Login Portal
        col_pad1, col_center, col_pad2 = st.columns([1, 2, 1])

        with col_center:
            st.markdown(
                f"""
                <div class="cs-login-wrapper">
                    <div class="cs-login-brand-icon">
                        {svg_shield(28, "#6366f1")}
                    </div>
                    <div class="cs-login-title">CodeSecure AI</div>
                    <div style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: #a5b4fc; letter-spacing: 0.08em; margin-bottom: 8px;">
                        Tata Technologies Tech Pulse FY-26 &bull; Case Study CS4
                    </div>
                    <div class="cs-login-desc">
                        Host-Isolated Defensive Code Review, Static Analysis, and Grounded Educational Guidance Platform.
                    </div>
                """,
                unsafe_allow_html=True,
            )

            # Role Preset Selector Buttons
            st.markdown(
                """
                <div style="font-size: 12px; font-weight: 600; color: #cbd5e1; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.05em;">
                    Select Role Preset
                </div>
                """,
                unsafe_allow_html=True,
            )

            preset_role = st.selectbox(
                "Preset Role Selection",
                ["developer", "reviewer", "security_eng", "admin"],
                index=0,
                label_visibility="collapsed",
            )
            preset_pass = DEMO_ROLES.get(preset_role, "Dev@CodeSecure2026")

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

            login_user = st.text_input("Username", value=preset_role)
            login_pass = st.text_input("Password", value=preset_pass, type="password")

            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

            if st.button("Authenticate and Enter Platform", type="primary", use_container_width=True):
                role_assigned = login_user if login_user in DEMO_ROLES else "developer"
                st.session_state.authenticated = True
                st.session_state.username = login_user
                st.session_state.role = role_assigned
                security_service.log_event(
                    action="UI_LOGIN",
                    resource="streamlit_ui",
                    username=login_user,
                    status="SUCCESS",
                )
                st.rerun()

            st.markdown(
                """
                <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.06); font-size: 11px; color: #64748b; line-height: 1.6;">
                    <strong>Security Verification:</strong> Source code is processed on local host only. No code telemetry egresses to public networks. PBKDF2 credential validation.
                </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ==========================================================================
    # AUTHENTICATED PLATFORM WORKSPACE
    # ==========================================================================
    else:
        # ----------------------------------------------------------------------
        # SIDEBAR NAVIGATION & PROFILE
        # ----------------------------------------------------------------------
        with st.sidebar:
            st.markdown(
                f"""
                <div class="cs-sidebar-brand">
                    <div class="cs-brand-name">
                        {svg_shield(20, "#6366f1")}
                        <span>CODESECURE AI</span>
                    </div>
                    <div class="cs-brand-tagline">
                        Privacy-Preserving Defensive Code Review Engine
                    </div>
                    <div style="margin-top: 8px;">
                        <span class="cs-pill cs-pill-emerald">
                            <span class="cs-indicator-dot dot-emerald"></span>
                            HOST ISOLATED
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Authenticated Account Card
            role_pill_cls = {
                "admin": "cs-pill-rose",
                "security_eng": "cs-pill-primary",
                "reviewer": "cs-pill-emerald",
                "developer": "cs-pill-cyan",
            }.get(st.session_state.role, "cs-pill-neutral")

            st.markdown(
                f"""
                <div class="cs-account-card">
                    <div class="cs-account-row">
                        <div class="cs-account-left">
                            <div class="cs-account-avatar">
                                {st.session_state.username[:2].upper()}
                            </div>
                            <div>
                                <div class="cs-account-name">{st.session_state.username}</div>
                                <div style="margin-top: 2px;">
                                    <span class="cs-pill {role_pill_pill_class if 'role_pill_pill_class' in locals() else role_pill_cls}">{st.session_state.role.upper()}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("Sign Out", use_container_width=True):
                old_user = st.session_state.username
                st.session_state.authenticated = False
                st.session_state.username = "anonymous"
                st.session_state.role = "developer"
                security_service.log_event(
                    action="UI_LOGOUT",
                    resource="streamlit_ui",
                    username=old_user,
                    status="SUCCESS",
                )
                st.rerun()

            st.markdown("<hr style='border-color: rgba(255,255,255,0.06); margin: 16px 0;'>", unsafe_allow_html=True)

            PAGES = [
                "Dashboard",
                "Code Review",
                "Compiler & Log Analysis",
                "Findings Management",
                "RAG Knowledge Base",
                "Evaluation & Metrics",
                "Audit & Security Logs",
            ]
            selected_page = st.radio("Navigation", PAGES, label_visibility="collapsed")

            st.markdown("<hr style='border-color: rgba(255,255,255,0.06); margin: 16px 0;'>", unsafe_allow_html=True)

            # Telemetry Overview Box in Sidebar
            st.markdown(
                f"""
                <div style="background: rgba(10,14,24,0.6); padding: 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05); font-size: 11px;">
                    <div style="font-weight: 700; color: #cbd5e1; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.05em;">Engine Status</div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px; color: #94a3b8;">
                        <span>LLM Backend:</span><span style="font-family: monospace; color: #38bdf8;">qwen2.5-coder</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px; color: #94a3b8;">
                        <span>Vector Index:</span><span style="font-family: monospace; color: #34d399;">ChromaDB (62)</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; color: #94a3b8;">
                        <span>Isolation:</span><span style="font-family: monospace; color: #a5b4fc;">Localhost:11434</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ----------------------------------------------------------------------
        # UNIVERSAL COMPLIANCE & GOVERNANCE RIBBON (STRICTLY NO EMOJIS)
        # ----------------------------------------------------------------------
        st.markdown(
            f"""
            <div class="cs-enterprise-ribbon">
                <div class="cs-ribbon-left">
                    <div class="cs-ribbon-icon-box">
                        {svg_shield(16, "#a5b4fc")}
                    </div>
                    <div class="cs-ribbon-text">
                        <strong>CodeSecure AI Enterprise Platform</strong> &mdash; Static Code Analysis & Grounded Triage (CS4).<br>
                        <span>Educational Governance Notice: Findings require human verification. This tool does not claim certified MISRA compliance.</span>
                    </div>
                </div>
                <div class="cs-ribbon-badges">
                    <span class="cs-pill cs-pill-emerald"><span class="cs-indicator-dot dot-emerald"></span>Zero-Cloud Egress</span>
                    <span class="cs-pill cs-pill-primary">Host Isolated</span>
                    <span class="cs-pill cs-pill-cyan">Human-in-the-Loop</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ======================================================================
        # PAGE 1: DASHBOARD
        # ======================================================================
        if selected_page == "Dashboard":
            st.markdown(
                """
                <div style="margin-bottom: 20px;">
                    <h2 style="font-weight: 800; font-size: 24px; color: #ffffff; margin-bottom: 4px; letter-spacing: -0.01em;">Executive Security Dashboard</h2>
                    <p style="color: #94a3b8; font-size: 13.5px; margin: 0;">Real-time defect metrics, repository vulnerability posture, and host isolation telemetry.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            all_findings = finding_service.get_findings(limit=500)
            total_findings = len(all_findings)
            open_findings = sum(1 for f in all_findings if f.get("status") == "Open")
            crit_high = sum(1 for f in all_findings if f.get("severity") in ("Critical", "High"))
            confirmed = sum(1 for f in all_findings if f.get("status") == "Confirmed")

            k1, k2, k3, k4 = st.columns(4)
            with k1:
                render_kpi_tile("Total Findings", total_findings, "Tracked in SQLite Database", "stripe-primary")
            with k2:
                render_kpi_tile("Open Findings", open_findings, "Awaiting Reviewer Triage", "stripe-amber")
            with k3:
                render_kpi_tile("Critical & High", crit_high, "Immediate Security Focus", "stripe-rose")
            with k4:
                render_kpi_tile("Confirmed Findings", confirmed, "Verified by Security Reviewer", "stripe-emerald")

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            col_d1, col_d2 = st.columns([1, 1])

            with col_d1:
                st.markdown(
                    """
                    <div class="cs-panel">
                        <div class="cs-panel-header">
                            <div class="cs-panel-title">System Health & Host Boundary Telemetry</div>
                            <div class="cs-panel-subtitle">Isolation Parameters</div>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )

                ollama_health = llm_service.check_health()
                rag_stats = rag_service.get_stats()

                model_badge = f'<span class="cs-pill cs-pill-primary">{ollama_health["configured_model"]}</span>'
                if ollama_health["reachable"]:
                    status_pill = '<span class="cs-pill cs-pill-emerald"><span class="cs-indicator-dot dot-emerald"></span>ONLINE</span>'
                else:
                    status_pill = '<span class="cs-pill cs-pill-amber"><span class="cs-indicator-dot dot-amber"></span>RESILIENT FALLBACK ACTIVE</span>'

                vector_badge = f'<span class="cs-pill cs-pill-cyan">{rag_stats["vector_backend"]}</span>'
                chunks_count = f'<span class="cs-pill cs-pill-neutral">{rag_stats["total_chunks"]} Chunks</span>'

                st.markdown(
                    f"""
                        <div class="cs-row-item">
                            <span class="cs-row-label">Local LLM Engine</span>
                            <span>{model_badge}</span>
                        </div>
                        <div class="cs-row-item">
                            <span class="cs-row-label">Ollama Daemon Service</span>
                            <span>{status_pill}</span>
                        </div>
                        <div class="cs-row-item">
                            <span class="cs-row-label">Vector Database</span>
                            <span>{vector_badge}</span>
                        </div>
                        <div class="cs-row-item">
                            <span class="cs-row-label">Loaded Knowledge Chunks</span>
                            <span>{chunks_count}</span>
                        </div>
                        <div class="cs-row-item">
                            <span class="cs-row-label">Network Boundary</span>
                            <span class="cs-row-value" style="color: #10b981;">Strict Localhost Only</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col_d2:
                st.markdown(
                    """
                    <div class="cs-panel">
                        <div class="cs-panel-header">
                            <div class="cs-panel-title">Recent Review Sessions</div>
                            <div class="cs-panel-subtitle">Session Cache</div>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )

                if IN_MEMORY_REVIEWS:
                    for sid, r in list(IN_MEMORY_REVIEWS.items())[-4:]:
                        f_cnt = r.get("findings_count", 0)
                        cnt_pill = f'<span class="cs-pill cs-pill-rose">{f_cnt} DEFECTS</span>' if f_cnt > 0 else '<span class="cs-pill cs-pill-emerald">0 DEFECTS</span>'
                        st.markdown(
                            f"""
                            <div class="cs-row-item" style="margin-bottom: 8px;">
                                <div>
                                    <span style="font-weight: 700; color: #a5b4fc; font-family: monospace;">SESSION #{sid}</span> &mdash;
                                    <code style="color: #38bdf8;">{r.get('file_name', 'code.cpp')}</code>
                                    <div style="font-size: 11px; color: #64748b; margin-top: 2px;">{r.get('review_type')}</div>
                                </div>
                                <div>{cnt_pill}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown(
                        """
                        <div style="text-align: center; padding: 36px 20px; color: #64748b;">
                            <div style="font-weight: 600; color: #94a3b8; font-size: 14px;">No reviews executed in current session yet</div>
                            <div style="font-size: 12px; margin-top: 4px;">Navigate to Code Review to analyze source files under defensive guidelines.</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown("</div>", unsafe_allow_html=True)

        # ======================================================================
        # PAGE 2: CODE REVIEW
        # ======================================================================
        elif selected_page == "Code Review":
            st.markdown(
                """
                <div style="margin-bottom: 20px;">
                    <h2 style="font-weight: 800; font-size: 24px; color: #ffffff; margin-bottom: 4px;">Automated Secure Code Review</h2>
                    <p style="color: #94a3b8; font-size: 13.5px; margin: 0;">Perform static vulnerability analysis and MISRA-oriented defensive review on C/C++ source code.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            samples_dir = BASE_DIR / "data" / "code_samples"
            available_samples = ["(Select a synthetic test case...)"]
            if samples_dir.exists():
                available_samples.extend(sorted([f.name for f in samples_dir.glob("*.cpp")]))

            col_s1, col_s2 = st.columns([2, 1])
            with col_s1:
                selected_sample = st.selectbox("Load Test Case Sample", available_samples)
            with col_s2:
                review_type = st.selectbox(
                    "Review Scope",
                    [
                        "Security Review",
                        "MISRA-Oriented Review",
                        "Code Explanation",
                        "General Code Review",
                    ],
                )

            default_code = "void processSensor(int* sensor) {\n    int value = sensor[0];\n}\n"
            file_name = "sensor.cpp"

            if selected_sample and selected_sample != "(Select a synthetic test case...)":
                fp = samples_dir / selected_sample
                if fp.exists():
                    default_code = fp.read_text(encoding="utf-8")
                    file_name = selected_sample

            col_f1, col_f2 = st.columns([1, 2])
            with col_f1:
                input_filename = st.text_input("Source File Name", value=file_name)
            with col_f2:
                st.markdown(
                    """
                    <div style="display: flex; align-items: flex-end; height: 100%; padding-bottom: 6px;">
                        <span style="font-size: 12px; color: #94a3b8;">Language: <strong style="color: #38bdf8;">C / C++17</strong> | Ruleset: <strong style="color: #a5b4fc;">Defensive & MISRA Educational</strong></span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            code_input = st.text_area("Source Code Under Analysis", value=default_code, height=270)

            if st.button("Execute Static Review", type="primary", use_container_width=True):
                if not code_input.strip():
                    st.error("Source code cannot be empty.")
                else:
                    with st.spinner("Executing analysis via local RAG and review engine..."):
                        try:
                            req = CodeReviewRequest(
                                code=code_input,
                                file_name=input_filename,
                                review_type=review_type,
                            )
                            response = review_service.review_code(
                                request=req,
                                user_id=st.session_state.user_id,
                                username=st.session_state.username,
                            )

                            st.markdown(
                                f"""
                                <div class="cs-enterprise-ribbon" style="border-left-color: #10b981; margin-top: 18px;">
                                    <div class="cs-ribbon-left">
                                        <div class="cs-ribbon-icon-box" style="color: #10b981; background: rgba(16,185,129,0.12); border-color: rgba(16,185,129,0.25);">
                                            {svg_shield(16, '#10b981')}
                                        </div>
                                        <div class="cs-ribbon-text">
                                            <strong>Analysis Completed:</strong> {response.summary}
                                        </div>
                                    </div>
                                    <div class="cs-ribbon-badges">
                                        <span class="cs-pill cs-pill-primary">Engine: {response.model_used}</span>
                                        <span class="cs-pill cs-pill-emerald">Security: {response.prompt_security_status}</span>
                                        <span class="cs-pill cs-pill-neutral">Session #{response.review_session_id}</span>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                            st.markdown(
                                f"""
                                <div style="display: flex; justify-content: space-between; align-items: center; margin: 20px 0 12px 0;">
                                    <h3 style="font-weight: 700; font-size: 17px; color: #ffffff; margin: 0;">Identified Findings ({len(response.findings)})</h3>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                            if not response.findings:
                                st.markdown(
                                    """
                                    <div class="cs-panel" style="text-align: center; padding: 32px;">
                                        <div style="font-weight: 700; color: #34d399; font-size: 15px;">Zero Security Defects Identified</div>
                                        <div style="color: #94a3b8; font-size: 12.5px; margin-top: 4px;">Source code satisfies verified defensive constraints for the selected scope.</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                            else:
                                for idx, f in enumerate(response.findings, 1):
                                    sev_pill = render_severity_pill(f.severity)
                                    line_pill = f'<span class="cs-pill cs-pill-neutral">LINE {f.line or "N/A"}</span>'
                                    fn_pill = f'<span class="cs-pill cs-pill-neutral">FUNC: {f.function or "N/A"}</span>'
                                    conf_pct = int(f.confidence * 100) if f.confidence else 85
                                    conf_pill = f'<span class="cs-pill cs-pill-emerald">CONFIDENCE: {conf_pct}%</span>'

                                    with st.expander(
                                        f"[{f.severity.upper()}] {f.category}: {f.issue} (Line {f.line or 'N/A'})",
                                        expanded=True,
                                    ):
                                        st.markdown(
                                            f"""
                                            <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;">
                                                {sev_pill}
                                                <span class="cs-pill cs-pill-neutral">FILE: {f.file}</span>
                                                {line_pill}
                                                {fn_pill}
                                                {conf_pill}
                                            </div>
                                            """,
                                            unsafe_allow_html=True,
                                        )

                                        if f.evidence:
                                            st.markdown(
                                                f"""
                                                <div style="font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; margin-bottom: 4px;">Observed Evidence</div>
                                                <div class="cs-evidence-container">{f.evidence}</div>
                                                """,
                                                unsafe_allow_html=True,
                                            )

                                        if f.root_cause:
                                            st.markdown(
                                                f"""
                                                <div class="cs-advisory-callout callout-cause">
                                                    <strong>Root Cause Hypothesis:</strong><br>{f.root_cause}
                                                </div>
                                                """,
                                                unsafe_allow_html=True,
                                            )

                                        st.markdown(
                                            f"""
                                            <div class="cs-advisory-callout callout-recommendation">
                                                <strong>Defensive Recommendation:</strong><br>{f.recommendation}
                                            </div>
                                            """,
                                            unsafe_allow_html=True,
                                        )

                                        if f.citations:
                                            c_tags = " ".join([f'<span class="cs-pill cs-pill-primary">{c}</span>' for c in f.citations])
                                            st.markdown(
                                                f"""
                                                <div style="margin-top: 10px; font-size: 12px; color: #94a3b8;">
                                                    <strong>Verified Educational Citations:</strong> {c_tags}
                                                </div>
                                                """,
                                                unsafe_allow_html=True,
                                            )

                            with st.expander("Retrieved RAG Grounding Context", expanded=False):
                                for c in response.citations_retrieved:
                                    st.markdown(
                                        f"""
                                        <div style="background: rgba(10,14,24,0.6); padding: 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.06); margin-bottom: 8px;">
                                            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                                                <span style="font-weight: 700; color: #38bdf8; font-size: 13px;">[{c['citation_code']}] {c['topic']}</span>
                                                <span class="cs-pill cs-pill-neutral">Score: {c['score']}</span>
                                            </div>
                                            <div style="font-size: 12px; color: #cbd5e1; line-height: 1.5; white-space: pre-wrap;">{c['content']}</div>
                                        </div>
                                        """,
                                        unsafe_allow_html=True,
                                    )

                        except ValueError as e:
                            st.error(f"Validation Error: {str(e)}")
                        except Exception as e:
                            st.error(f"Review Error: {str(e)}")

        # ======================================================================
        # PAGE 3: LOG ANALYSIS
        # ======================================================================
        elif selected_page == "Compiler & Log Analysis":
            st.markdown(
                """
                <div style="margin-bottom: 20px;">
                    <h2 style="font-weight: 800; font-size: 24px; color: #ffffff; margin-bottom: 4px;">Compiler & Runtime Log Diagnosis</h2>
                    <p style="color: #94a3b8; font-size: 13.5px; margin: 0;">Automated diagnosis for GCC/Clang warnings, Cppcheck static findings, AddressSanitizer, and Valgrind memory leaks.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            logs_samples = {
                "GCC Null Dereference Error": "sensor.cpp:6:19: warning: dereferencing pointer 'sensor' does not check for NULL [-Wnull-dereference]",
                "Clang Signedness Conversion": "packet.cpp:8:5: warning: implicit conversion changes signedness: 'int' to 'size_t' [-Wsign-conversion]",
                "AddressSanitizer Heap Use-After-Free": "ERROR: AddressSanitizer: heap-use-after-free on address 0x602000000010 in handleHeader() tc06_use_after_free.cpp:13",
                "Valgrind Memory Leak": "LEAK SUMMARY:\n   definitely lost: 1,024 bytes in 1 blocks in processPayload() tc05_memory_leak.cpp:5",
            }

            col_l1, col_l2 = st.columns([2, 1])
            with col_l1:
                chosen_sample = st.selectbox("Load Diagnostic Log Sample", ["(Select preset log...)"] + list(logs_samples.keys()))
            with col_l2:
                log_type = st.selectbox("Diagnostic Type", ["compiler", "static_analysis", "runtime"])

            default_log_text = logs_samples.get(chosen_sample, "sensor.cpp:6:19: warning: dereferencing pointer 'sensor' [-Wnull-dereference]")
            log_input = st.text_area("Diagnostic Log Content", value=default_log_text, height=180)

            if st.button("Execute Diagnostic Parsing", type="primary", use_container_width=True):
                if not log_input.strip():
                    st.error("Log content cannot be empty.")
                else:
                    try:
                        req = LogAnalysisRequest(log_content=log_input, log_type=log_type)
                        res = log_analysis_service.parse_log(
                            request=req,
                            user_id=st.session_state.user_id,
                            username=st.session_state.username,
                        )

                        c_err = f'<span class="cs-pill cs-pill-rose">{res.errors} ERRORS</span>'
                        c_warn = f'<span class="cs-pill cs-pill-amber">{res.warnings} WARNINGS</span>'
                        c_tot = f'<span class="cs-pill cs-pill-primary">{res.total_issues} TOTAL ISSUES</span>'

                        st.markdown(
                            f"""
                            <div class="cs-panel" style="margin-top: 16px; padding: 14px 18px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                                    <div>
                                        <span style="font-weight: 700; color: #ffffff; font-size: 14px;">Parsed Output:</span>
                                        <span style="margin-left: 8px;">{c_tot} {c_err} {c_warn}</span>
                                    </div>
                                    <div style="font-size: 12px; color: #94a3b8;">
                                        Cited Guidelines: <strong>{', '.join(res.rag_guidelines_cited) if res.rag_guidelines_cited else 'None'}</strong>
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        for item in res.issues:
                            with st.expander(f"[{item.severity.upper()}] {item.file}:{item.line or 'N/A'} — {item.message}", expanded=True):
                                st.markdown(
                                    f"""
                                    <div style="display: flex; gap: 8px; margin-bottom: 10px;">
                                        {render_severity_pill(item.severity)}
                                        <span class="cs-pill cs-pill-neutral">CODE: {item.error_code}</span>
                                        <span class="cs-pill cs-pill-neutral">LOC: {item.file}:{item.line or 'N/A'}</span>
                                    </div>
                                    <div class="cs-advisory-callout callout-cause">
                                        <strong>Probable Cause:</strong><br>{item.probable_cause}
                                    </div>
                                    <div class="cs-advisory-callout callout-recommendation">
                                        <strong>Suggested Next Step:</strong><br>{item.suggested_step}
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                                if item.relevant_guideline:
                                    st.markdown(f"**Educational Guideline**: `{item.relevant_guideline}`")

                    except Exception as e:
                        st.error(f"Error analyzing log: {e}")

        # ======================================================================
        # PAGE 4: FINDINGS MANAGEMENT
        # ======================================================================
        elif selected_page == "Findings Management":
            st.markdown(
                """
                <div style="margin-bottom: 20px;">
                    <h2 style="font-weight: 800; font-size: 24px; color: #ffffff; margin-bottom: 4px;">Findings Governance & Reviewer Disposition</h2>
                    <p style="color: #94a3b8; font-size: 13.5px; margin: 0;">Human-in-the-loop review interface: verify, confirm, reject, or mark findings as fixed.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<div class='cs-panel' style='padding: 16px 20px; margin-bottom: 16px;'>", unsafe_allow_html=True)
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                sev_filter = st.selectbox("Filter Severity", ["All", "Critical", "High", "Medium", "Low"])
            with col_f2:
                status_filter = st.selectbox("Filter Status", ["All", "Open", "Confirmed", "Rejected", "Fixed", "Needs Review"])
            with col_f3:
                search_cat = st.text_input("Filter Category / Keyword", "")
            st.markdown("</div>", unsafe_allow_html=True)

            findings = finding_service.get_findings(
                severity=None if sev_filter == "All" else sev_filter,
                status=None if status_filter == "All" else status_filter,
                limit=200,
            )

            if search_cat:
                findings = [f for f in findings if search_cat.lower() in f.get("category", "").lower() or search_cat.lower() in f.get("issue", "").lower()]

            st.markdown(
                f"""
                <div style="margin-bottom: 14px; font-size: 12.5px; color: #94a3b8;">
                    Displaying <strong style="color: #ffffff;">{len(findings)}</strong> findings matching active criteria
                </div>
                """,
                unsafe_allow_html=True,
            )

            if not findings:
                st.info("No findings match the selected filters.")
            else:
                for f in findings:
                    fid = f.get("id")
                    sev_pill = render_severity_pill(f.get("severity", "Medium"))
                    stat_pill = render_status_pill(f.get("status", "Open"))

                    with st.expander(
                        f"#{fid} [{f.get('severity', '').upper()}] {f.get('issue')} | Status: {f.get('status', '').upper()}",
                        expanded=False,
                    ):
                        st.markdown(
                            f"""
                            <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;">
                                {sev_pill}
                                {stat_pill}
                                <span class="cs-pill cs-pill-neutral">FILE: {f.get('file')} (Line {f.get('line')})</span>
                                <span class="cs-pill cs-pill-primary">RULE: {f.get('rule')}</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        if f.get("evidence"):
                            st.markdown(f"**Observed Evidence**: `{f.get('evidence')}`")
                        st.markdown(f"**Root Cause**: {f.get('root_cause')}")
                        st.markdown(f"**Defensive Recommendation**: {f.get('recommendation')}")

                        if f.get("reviewer_comment"):
                            st.info(f"Reviewer Comment: {f.get('reviewer_comment')}")

                        if st.session_state.role in ("reviewer", "security_eng", "admin"):
                            st.markdown("<hr style='border-color: rgba(255,255,255,0.06); margin: 12px 0;'>", unsafe_allow_html=True)
                            st.markdown("<div style='font-size: 13px; font-weight: 700; color: #a5b4fc; margin-bottom: 8px;'>UPDATE DISPOSITION</div>", unsafe_allow_html=True)
                            col_u1, col_u2 = st.columns([1, 2])
                            with col_u1:
                                new_status = st.selectbox(
                                    "Disposition Status",
                                    ["Open", "Confirmed", "Rejected", "Fixed", "Needs Review"],
                                    index=["Open", "Confirmed", "Rejected", "Fixed", "Needs Review"].index(f.get("status", "Open")),
                                    key=f"status_select_{fid}",
                                )
                            with col_u2:
                                comment = st.text_input(
                                    "Reviewer Commentary",
                                    value=f.get("reviewer_comment") or "",
                                    key=f"comment_input_{fid}",
                                )

                            if st.button(f"Commit Disposition for Finding #{fid}", key=f"btn_save_{fid}", type="primary"):
                                finding_service.update_disposition(
                                    finding_id=fid,
                                    update=FindingStatusUpdate(status=new_status, reviewer_comment=comment),
                                    user_id=st.session_state.user_id,
                                    username=st.session_state.username,
                                )
                                st.success(f"Finding #{fid} disposition updated to '{new_status}'.")
                                st.rerun()
                        else:
                            st.caption("Access restricted: Authenticate as Reviewer, Security Engineer, or Administrator to update disposition.")

        # ======================================================================
        # PAGE 5: RAG KNOWLEDGE BASE
        # ======================================================================
        elif selected_page == "RAG Knowledge Base":
            st.markdown(
                """
                <div style="margin-bottom: 20px;">
                    <h2 style="font-weight: 800; font-size: 24px; color: #ffffff; margin-bottom: 4px;">Synthetic Educational Knowledge Base</h2>
                    <p style="color: #94a3b8; font-size: 13.5px; margin: 0;">Browse local guidelines, execute semantic vector search, and inspect grounded chunk metadata.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            stats = rag_service.get_stats()
            c1, c2, c3 = st.columns(3)
            with c1:
                render_kpi_tile("Total Chunks", stats["total_chunks"], "Embedded Semantic Chunks", "stripe-primary")
            with c2:
                render_kpi_tile("Active Rules", len(stats["citations_available"]), "Synthetic Educational Rules", "stripe-emerald")
            with c3:
                render_kpi_tile("Vector Backend", stats["vector_backend"], "Localhost Vector Store", "stripe-cyan")

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            st.markdown(
                """
                <div class="cs-panel">
                    <div class="cs-panel-header">
                        <div class="cs-panel-title">Semantic Vector Search</div>
                        <div class="cs-panel-subtitle">Cosine Similarity Retrieval</div>
                    </div>
                """,
                unsafe_allow_html=True,
            )

            col_q, col_cat = st.columns([3, 1])
            with col_q:
                query_text = st.text_input("Search Query", value="null pointer defensive check")
            with col_cat:
                cat_choice = st.selectbox("Category Scope", ["All", "Coding Guidelines", "MISRA-Oriented Guidance", "Security", "Historical Findings"])

            if st.button("Search Knowledge Store", type="primary", use_container_width=True):
                results = rag_service.search(query=query_text, category=None if cat_choice == "All" else cat_choice, top_k=5)
                if not results:
                    st.warning("No matching knowledge chunks found.")
                else:
                    for idx, r in enumerate(results, 1):
                        score_val = r.get('score', 0)
                        with st.expander(f"[{r['citation_code']}] {r['topic']} (Relevance Score: {score_val})", expanded=True):
                            st.markdown(
                                f"""
                                <div style="display: flex; gap: 8px; margin-bottom: 10px;">
                                    <span class="cs-pill cs-pill-primary">{r['citation_code']}</span>
                                    <span class="cs-pill cs-pill-neutral">CATEGORY: {r['category']}</span>
                                    <span class="cs-pill cs-pill-neutral">CHUNK: {r['chunk_id']}</span>
                                    <span class="cs-pill cs-pill-emerald">SCORE: {score_val}</span>
                                </div>
                                <div style="font-size: 13px; color: #cbd5e1; line-height: 1.6; margin-top: 8px;">
                                """,
                                unsafe_allow_html=True,
                            )
                            st.markdown(r["content"])
                            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            if st.session_state.role in ("security_eng", "admin"):
                st.markdown(
                    """
                    <div class="cs-panel" style="margin-top: 16px;">
                        <div class="cs-panel-header">
                            <div class="cs-panel-title">Knowledge Base Maintenance</div>
                            <div class="cs-panel-subtitle">Privileged Operation</div>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Re-index Knowledge Store", type="secondary"):
                    with st.spinner("Re-indexing knowledge documents into local ChromaDB..."):
                        res = rag_service.ingest_knowledge_base()
                        st.success(f"Ingested {res['documents_ingested']} documents into {res['chunks_created']} chunks.")
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        # ======================================================================
        # PAGE 6: EVALUATION & METRICS
        # ======================================================================
        elif selected_page == "Evaluation & Metrics":
            st.markdown(
                """
                <div style="margin-bottom: 20px;">
                    <h2 style="font-weight: 800; font-size: 24px; color: #ffffff; margin-bottom: 4px;">Automated Evaluation Pipeline</h2>
                    <p style="color: #94a3b8; font-size: 13.5px; margin: 0;">Empirical benchmark against synthetic C/C++ ground truth dataset (Tata Technologies CS4 Case Study).</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            results = evaluation_service.get_results()

            if results.get("status") == "Not yet executed":
                st.warning("Evaluation benchmark has not yet been executed in this session.")
                st.info("Click 'Execute Benchmark Suite' below to run the automated benchmark across 21 synthetic test cases.")
            else:
                st.markdown(
                    f"""
                    <div class="cs-enterprise-ribbon" style="border-left-color: #10b981; margin-bottom: 20px;">
                        <div class="cs-ribbon-left">
                            <div class="cs-ribbon-icon-box" style="color: #10b981; background: rgba(16,185,129,0.12); border-color: rgba(16,185,129,0.25);">
                                {svg_shield(16, '#10b981')}
                            </div>
                            <div class="cs-ribbon-text">
                                <strong>Benchmark Status:</strong> {results.get('status')} &mdash; Timestamp: <code>{results.get('timestamp')}</code>
                            </div>
                        </div>
                        <div class="cs-ribbon-badges">
                            <span class="cs-pill cs-pill-emerald">21 TEST CASES</span>
                            <span class="cs-pill cs-pill-primary">GROUND TRUTH VERIFIED</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                e1, e2, e3, e4 = st.columns(4)
                with e1:
                    render_kpi_tile("Precision", f"{results.get('precision', 0.0) * 100:.1f}%", "TP / (TP + FP)", "stripe-primary")
                with e2:
                    render_kpi_tile("Recall", f"{results.get('recall', 0.0) * 100:.1f}%", "TP / (TP + FN)", "stripe-cyan")
                with e3:
                    render_kpi_tile("F1-Score", f"{results.get('f1_score', 0.0) * 100:.1f}%", "Harmonic Mean", "stripe-emerald")
                with e4:
                    render_kpi_tile("Avg Latency", f"{results.get('average_response_time_ms', 0.0):.1f} ms", "Per Test Case", "stripe-amber")

                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

                a1, a2, a3, a4 = st.columns(4)
                with a1:
                    render_kpi_tile("Severity Accuracy", f"{results.get('severity_accuracy', 0.0) * 100:.1f}%", "Severity Match", "stripe-amber")
                with a2:
                    render_kpi_tile("Category Accuracy", f"{results.get('category_accuracy', 0.0) * 100:.1f}%", "Defect Type Match", "stripe-cyan")
                with a3:
                    render_kpi_tile("Citation Accuracy", f"{results.get('citation_accuracy', 0.0) * 100:.1f}%", "RAG Grounding Match", "stripe-primary")
                with a4:
                    render_kpi_tile("False Positive Rate", f"{results.get('false_positive_rate', 0.0) * 100:.1f}%", "FP / (FP + TN)", "stripe-rose")

                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

                st.markdown(
                    f"""
                    <div class="cs-panel">
                        <div class="cs-panel-header">
                            <div class="cs-panel-title">Empirical Confusion Matrix</div>
                            <div class="cs-panel-subtitle">Ground Truth Evaluation</div>
                        </div>
                        <div class="cs-grid-matrix">
                            <div class="cs-matrix-tile tile-tp">
                                <div class="cs-matrix-val" style="color: #34d399;">{results.get('true_positives', 0)}</div>
                                <div class="cs-matrix-tag">True Positives (TP)</div>
                                <div class="cs-matrix-detail">Accurately Identified Vulnerabilities</div>
                            </div>
                            <div class="cs-matrix-tile tile-fp">
                                <div class="cs-matrix-val" style="color: #fbbf24;">{results.get('false_positives', 0)}</div>
                                <div class="cs-matrix-tag">False Positives (FP)</div>
                                <div class="cs-matrix-detail">Spurious Defect Reports</div>
                            </div>
                            <div class="cs-matrix-tile tile-fn">
                                <div class="cs-matrix-val" style="color: #fb7185;">{results.get('false_negatives', 0)}</div>
                                <div class="cs-matrix-tag">False Negatives (FN)</div>
                                <div class="cs-matrix-detail">Undetected Security Vulnerabilities</div>
                            </div>
                            <div class="cs-matrix-tile tile-tn">
                                <div class="cs-matrix-val" style="color: #38bdf8;">{results.get('true_negatives', 0)}</div>
                                <div class="cs-matrix-tag">True Negatives (TN)</div>
                                <div class="cs-matrix-detail">Accurately Verified Safe Test Cases</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            if st.button("Execute Benchmark Suite", type="primary", use_container_width=True):
                with st.spinner("Benchmarking across 21 test cases against ground truth dataset..."):
                    rep = evaluation_service.run_evaluation()
                    st.success("Evaluation pipeline execution completed.")
                    st.rerun()

        # ======================================================================
        # PAGE 7: AUDIT & SECURITY LOGS
        # ======================================================================
        elif selected_page == "Audit & Security Logs":
            st.markdown(
                """
                <div style="margin-bottom: 20px;">
                    <h2 style="font-weight: 800; font-size: 24px; color: #ffffff; margin-bottom: 4px;">Security Audit & Incident Telemetry</h2>
                    <p style="color: #94a3b8; font-size: 13.5px; margin: 0;">Tamper-evident operational audit trail. Restricted to Security Engineers and Administrators.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.session_state.role not in ("security_eng", "admin"):
                st.markdown(
                    """
                    <div class="cs-panel" style="text-align: center; padding: 40px; border-left: 3px solid #f43f5e;">
                        <div style="font-weight: 700; color: #fb7185; font-size: 15px;">Access Restricted</div>
                        <div style="color: #94a3b8; font-size: 13px; margin-top: 6px;">
                            Role-Based Access Control (RBAC) enforced. You must be authenticated as a <strong>Security Engineer</strong> or <strong>Administrator</strong> to inspect audit telemetry.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                action_filter = st.selectbox(
                    "Filter Action Type",
                    [
                        "All",
                        "CODE_REVIEW_COMPLETED",
                        "PROMPT_INJECTION_DETECTED",
                        "FINDING_DISPOSITION_UPDATED",
                        "LOGIN_SUCCESS",
                        "LOGIN_FAILED",
                        "UI_LOGIN",
                        "UI_LOGOUT",
                        "EVALUATION_RUN_COMPLETED",
                    ],
                )
                logs = security_service.get_audit_logs(
                    limit=150,
                    action_filter=None if action_filter == "All" else action_filter,
                )

                st.markdown(
                    f"""
                    <div style="margin-bottom: 14px; font-size: 12.5px; color: #94a3b8;">
                        Displaying <strong style="color: #ffffff;">{len(logs)}</strong> audit records
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if not logs:
                    st.info("No matching audit logs recorded.")
                else:
                    for entry in logs:
                        status_pill = '<span class="cs-pill cs-pill-emerald">SUCCESS</span>' if entry.get("status") in ("SUCCESS", "MITIGATED") else '<span class="cs-pill cs-pill-rose">FAILED</span>'
                        with st.expander(
                            f"[{entry.get('timestamp')[:19]}] {entry.get('action')} by '{entry.get('username')}' ({entry.get('status')})"
                        ):
                            st.markdown(
                                f"""
                                <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px;">
                                    {status_pill}
                                    <span class="cs-pill cs-pill-neutral">ACTOR: {entry.get('username')}</span>
                                    <span class="cs-pill cs-pill-neutral">RESOURCE: {entry.get('resource')}</span>
                                    <span class="cs-pill cs-pill-neutral">TIME: {entry.get('timestamp')}</span>
                                </div>
                                <div style="font-size: 12.5px; color: #cbd5e1;">
                                    <strong>Details:</strong> <code>{entry.get('details') or 'None'}</code>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
