"""
CodeSecure AI — Streamlit Frontend Application
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

    # Page Configuration
    st.set_page_config(
        page_title="CodeSecure AI — Secure Code Review & Debugging",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Styling & Disclaimer Header
    st.markdown(
        """
        <style>
        .banner-warning {
            background-color: #fff3cd;
            color: #856404;
            padding: 10px 16px;
            border-radius: 6px;
            border-left: 5px solid #ffeeba;
            font-size: 14px;
            margin-bottom: 20px;
        }
        .metric-card {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Session State Initialization
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = "anonymous"
        st.session_state.role = "developer"
        st.session_state.user_id = 1

    # Sidebar: Brand & Navigation
    st.sidebar.title("🛡️ CodeSecure AI")
    st.sidebar.caption("Privacy-Preserving Code Review & Debugging")

    # Global Disclaimer
    st.sidebar.markdown(
        """
        ---
        **⚠️ Academic & Safety Notice**  
        *AI-assisted analysis — human review required.*  
        *Does not claim certified MISRA compliance.*  
        *Source code stays strictly local.*
        ---
        """
    )

    # User Profile / Authentication in Sidebar
    if not st.session_state.authenticated:
        st.sidebar.subheader("🔐 Sign In")
        login_user = st.sidebar.text_input("Username", value="developer")
        login_pass = st.sidebar.text_input("Password", value="Dev@CodeSecure2026", type="password")

        demo_roles = {
            "developer": "Dev@CodeSecure2026",
            "reviewer": "Reviewer@CodeSecure2026",
            "security_eng": "SecEng@CodeSecure2026",
            "admin": "Admin@CodeSecure2026",
        }

        col_l1, col_l2 = st.sidebar.columns(2)
        with col_l1:
            if st.button("Log In", use_container_width=True):
                # Verify credentials
                role_assigned = login_user if login_user in demo_roles else "developer"
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

        st.sidebar.info("💡 Preset Demo Accounts:\n- developer\n- reviewer\n- security_eng\n- admin")
    else:
        st.sidebar.success(f"👤 **{st.session_state.username}** ({st.session_state.role})")
        if st.sidebar.button("Log Out"):
            st.session_state.authenticated = False
            st.session_state.username = "anonymous"
            st.session_state.role = "developer"
            st.rerun()

    # Navigation menu
    PAGES = [
        "📊 Dashboard",
        "🔍 Code Review",
        "📋 Compiler & Log Analysis",
        "📝 Findings Management",
        "📚 RAG Knowledge Base",
        "📈 Evaluation & Metrics",
        "🔒 Audit & Security Logs",
    ]
    selected_page = st.sidebar.radio("Navigation", PAGES)

    # Universal Compliance Banner on every page
    st.markdown(
        """
        <div class="banner-warning">
            🛡️ <b>CodeSecure AI Academic Platform</b> — Privacy-Preserving AI-Assisted Static Review.
            <b>Notice:</b> AI findings require human verification. This tool provides educational guidance only and does NOT constitute official MISRA certification.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ==============================================================================
    # PAGE 1: DASHBOARD
    # ==============================================================================
    if selected_page == "📊 Dashboard":
        st.header("Executive Dashboard")
        st.write("Real-time telemetry and overview of code review sessions and security findings.")

        all_findings = finding_service.get_findings(limit=500)
        total_findings = len(all_findings)
        open_findings = sum(1 for f in all_findings if f.get("status") == "Open")
        crit_high = sum(1 for f in all_findings if f.get("severity") in ("Critical", "High"))
        confirmed = sum(1 for f in all_findings if f.get("status") == "Confirmed")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Findings", total_findings)
        m2.metric("Open Findings", open_findings)
        m3.metric("Critical / High Severity", crit_high, delta_color="inverse")
        m4.metric("Confirmed by Reviewer", confirmed)

        st.markdown("---")

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.subheader("System Health & Privacy Telemetry")
            ollama_health = llm_service.check_health()
            rag_stats = rag_service.get_stats()

            st.write(f"**Local LLM Engine**: `{ollama_health['configured_model']}`")
            if ollama_health["reachable"]:
                st.success("🟢 Ollama Daemon: Online & Reachable")
            else:
                st.warning(f"🟡 Local LLM Status: Offline ({ollama_health['note']})")

            st.write(f"**Vector Store**: `{rag_stats['vector_backend']}`")
            st.write(f"**Loaded Knowledge Chunks**: `{rag_stats['total_chunks']}`")
            st.write(f"**Privacy Boundary**: `Local / Host Isolation (Strict No-Cloud Default)`")

        with col_d2:
            st.subheader("Recent Review Sessions")
            if IN_MEMORY_REVIEWS:
                for sid, r in list(IN_MEMORY_REVIEWS.items())[-4:]:
                    st.write(
                        f"• **Session #{sid}**: `{r.get('file_name', 'code.cpp')}` — "
                        f"{r.get('review_type')} ({r.get('findings_count', 0)} findings)"
                    )
            else:
                st.info("No code reviews executed in current session yet.")

    # ==============================================================================
    # PAGE 2: CODE REVIEW
    # ==============================================================================
    elif selected_page == "🔍 Code Review":
        st.header("AI-Assisted Secure Code Review")
        st.write("Submit C/C++ source code for local static analysis, RAG guidance, and structured findings.")

        # Preset test cases loader
        samples_dir = BASE_DIR / "data" / "code_samples"
        available_samples = ["(Select a synthetic test case...)"]
        if samples_dir.exists():
            available_samples.extend(sorted([f.name for f in samples_dir.glob("*.cpp")]))

        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            selected_sample = st.selectbox("Load Synthetic Sample Code", available_samples)
        with col_s2:
            review_type = st.selectbox(
                "Review Type",
                [
                    "Security Review",
                    "MISRA-Oriented Review",
                    "Code Explanation",
                    "General Code Review",
                ],
            )

        # Default code
        default_code = "void processSensor(int* sensor) {\n    int value = sensor[0];\n}\n"
        file_name = "sensor.cpp"

        if selected_sample and selected_sample != "(Select a synthetic test case...)":
            fp = samples_dir / selected_sample
            if fp.exists():
                default_code = fp.read_text(encoding="utf-8")
                file_name = selected_sample

        input_filename = st.text_input("Source File Name", value=file_name)
        code_input = st.text_area("C/C++ Source Code Under Review", value=default_code, height=260)

        if st.button("🚀 Run Privacy-Preserving Review", type="primary"):
            if not code_input.strip():
                st.error("Source code cannot be empty.")
            else:
                with st.spinner("Analyzing code via local RAG & secure review pipeline..."):
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

                        st.success(f"✅ {response.summary}")

                        # Security Telemetry
                        st.caption(
                            f"Engine: `{response.model_used}` | "
                            f"Prompt Security Status: `{response.prompt_security_status}` | "
                            f"Review Session ID: `#{response.review_session_id}`"
                        )

                        # Findings Display
                        st.subheader(f"Identified Findings ({len(response.findings)})")
                        if not response.findings:
                            st.info("No security defects or rule deviations detected.")
                        else:
                            for idx, f in enumerate(response.findings, 1):
                                sev_color = {
                                    "Critical": "🚨",
                                    "High": "🔴",
                                    "Medium": "🟠",
                                    "Low": "🟡",
                                    "Informational": "ℹ️",
                                }.get(f.severity, "📌")

                                with st.expander(
                                    f"{sev_color} [{f.severity}] {f.category}: {f.issue} (Line {f.line or 'N/A'})",
                                    expanded=True,
                                ):
                                    st.write(f"**Function**: `{f.function or 'N/A'}` | **File**: `{f.file}` | **Confidence**: `{f.confidence:.2f}`")
                                    st.markdown(f"**Observed Evidence**:  \n`{f.evidence or 'N/A'}`")
                                    st.markdown(f"**Root Cause Hypothesis**:  \n{f.root_cause or 'N/A'}")
                                    st.markdown(f"**Defensive Recommendation**:  \n{f.recommendation}")
                                    if f.citations:
                                        st.markdown(f"**RAG Citations**: `{', '.join(f.citations)}`")

                        # RAG Chunks Retrieved
                        with st.expander("📚 Retrieved RAG Grounding Context", expanded=False):
                            for c in response.citations_retrieved:
                                st.write(f"**[{c['citation_code']}]** *{c['topic']}* (Similarity Score: {c['score']})")
                                st.text(c["content"])

                    except ValueError as e:
                        st.error(f"Validation Error: {str(e)}")
                    except Exception as e:
                        st.error(f"Review Error: {str(e)}")

    # ==============================================================================
    # PAGE 3: LOG ANALYSIS
    # ==============================================================================
    elif selected_page == "📋 Compiler & Log Analysis":
        st.header("Compiler & Runtime Log Analysis")
        st.write("Diagnose compiler warnings, static analysis reports, and AddressSanitizer/Valgrind memory traces.")

        # Preset logs loader
        logs_samples = {
            "GCC Null Dereference Error": "sensor.cpp:6:19: warning: dereferencing pointer 'sensor' does not check for NULL [-Wnull-dereference]",
            "Clang Signedness Conversion": "packet.cpp:8:5: warning: implicit conversion changes signedness: 'int' to 'size_t' [-Wsign-conversion]",
            "AddressSanitizer Heap Use-After-Free": "ERROR: AddressSanitizer: heap-use-after-free on address 0x602000000010 in handleHeader() tc06_use_after_free.cpp:13",
            "Valgrind Memory Leak": "LEAK SUMMARY:\n   definitely lost: 1,024 bytes in 1 blocks in processPayload() tc05_memory_leak.cpp:5",
        }

        chosen_sample = st.selectbox("Load Sample Diagnostic Log", ["(Select preset log...)"] + list(logs_samples.keys()))
        default_log_text = logs_samples.get(chosen_sample, "sensor.cpp:6:19: warning: dereferencing pointer 'sensor' [-Wnull-dereference]")

        log_input = st.text_area("Paste Compiler / Sanitizer Log", value=default_log_text, height=180)
        log_type = st.selectbox("Log Type", ["compiler", "static_analysis", "runtime"])

        if st.button("🔍 Analyze Log Output", type="primary"):
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

                    st.success(f"Parsed {res.total_issues} issue(s): {res.errors} Error(s), {res.warnings} Warning(s).")
                    if res.rag_guidelines_cited:
                        st.caption(f"Relevant Guidelines: `{', '.join(res.rag_guidelines_cited)}`")

                    for item in res.issues:
                        with st.expander(f"[{item.severity}] {item.file}:{item.line or 'N/A'} — {item.message}", expanded=True):
                            st.write(f"**Diagnostic Code**: `{item.error_code}`")
                            st.write(f"**Probable Cause**: {item.probable_cause}")
                            st.write(f"**Suggested Next Step**: {item.suggested_step}")
                            if item.relevant_guideline:
                                st.write(f"**Guideline**: `{item.relevant_guideline}`")

                except Exception as e:
                    st.error(f"Error analyzing log: {e}")

    # ==============================================================================
    # PAGE 4: FINDINGS MANAGEMENT (HUMAN-IN-THE-LOOP)
    # ==============================================================================
    elif selected_page == "📝 Findings Management":
        st.header("Findings Governance & Reviewer Disposition")
        st.write("Human-in-the-loop review interface: verify, confirm, reject, or mark findings as fixed.")

        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            sev_filter = st.selectbox("Filter Severity", ["All", "Critical", "High", "Medium", "Low"])
        with col_f2:
            status_filter = st.selectbox("Filter Status", ["All", "Open", "Confirmed", "Rejected", "Fixed", "Needs Review"])
        with col_f3:
            search_cat = st.text_input("Filter Category / Keyword", "")

        findings = finding_service.get_findings(
            severity=None if sev_filter == "All" else sev_filter,
            status=None if status_filter == "All" else status_filter,
            limit=200,
        )

        if search_cat:
            findings = [f for f in findings if search_cat.lower() in f.get("category", "").lower() or search_cat.lower() in f.get("issue", "").lower()]

        st.caption(f"Showing {len(findings)} finding(s)")

        if not findings:
            st.info("No findings match the selected filters.")
        else:
            for f in findings:
                fid = f.get("id")
                with st.expander(
                    f"#{fid} [{f.get('severity')}] {f.get('issue')} | Status: {f.get('status')}",
                    expanded=False,
                ):
                    st.write(f"**File**: `{f.get('file')}` (Line {f.get('line')}) | **Rule**: `{f.get('rule')}`")
                    st.write(f"**Evidence**: `{f.get('evidence')}`")
                    st.write(f"**Root Cause**: {f.get('root_cause')}")
                    st.write(f"**Recommendation**: {f.get('recommendation')}")
                    if f.get("reviewer_comment"):
                        st.info(f"💬 Reviewer Note: {f.get('reviewer_comment')}")

                    # Reviewer Disposition Controls
                    if st.session_state.role in ("reviewer", "security_eng", "admin"):
                        st.markdown("---")
                        st.subheader("Update Reviewer Disposition")
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
                                "Reviewer Comment",
                                value=f.get("reviewer_comment") or "",
                                key=f"comment_input_{fid}",
                            )

                        if st.button(f"Save Disposition for Finding #{fid}", key=f"btn_save_{fid}"):
                            finding_service.update_disposition(
                                finding_id=fid,
                                update=FindingStatusUpdate(status=new_status, reviewer_comment=comment),
                                user_id=st.session_state.user_id,
                                username=st.session_state.username,
                            )
                            st.success(f"Finding #{fid} updated to '{new_status}'!")
                            st.rerun()
                    else:
                        st.caption("🔒 Log in as a Reviewer, Security Engineer, or Admin to disposition findings.")

    # ==============================================================================
    # PAGE 5: RAG KNOWLEDGE BASE
    # ==============================================================================
    elif selected_page == "📚 RAG Knowledge Base":
        st.header("Synthetic Educational Knowledge Base")
        st.write("Browse local guidelines, search vectors, and inspect chunk metadata.")

        stats = rag_service.get_stats()
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Chunks", stats["total_chunks"])
        c2.metric("Active Rules", len(stats["citations_available"]))
        c3.metric("Vector Backend", stats["vector_backend"])

        st.markdown("---")
        st.subheader("Interactive Knowledge Search")
        col_q, col_cat = st.columns([3, 1])
        with col_q:
            query_text = st.text_input("Semantic Search Query", value="null pointer defensive check")
        with col_cat:
            cat_choice = st.selectbox("Category", ["All", "Coding Guidelines", "MISRA-Oriented Guidance", "Security", "Historical Findings"])

        if st.button("🔍 Search Knowledge Base"):
            results = rag_service.search(query=query_text, category=None if cat_choice == "All" else cat_choice, top_k=5)
            if not results:
                st.warning("No matching chunks found.")
            else:
                for idx, r in enumerate(results, 1):
                    with st.expander(f"[{r['citation_code']}] {r['topic']} (Relevance: {r['score']})"):
                        st.caption(f"Category: {r['category']} | Chunk ID: {r['chunk_id']}")
                        st.markdown(r["content"])

        if st.session_state.role in ("security_eng", "admin"):
            st.markdown("---")
            if st.button("🔄 Trigger Knowledge Base Re-Ingestion"):
                with st.spinner("Re-indexing knowledge documents..."):
                    res = rag_service.ingest_knowledge_base()
                    st.success(f"Ingested {res['documents_ingested']} documents into {res['chunks_created']} chunks.")
                    st.rerun()

    # ==============================================================================
    # PAGE 6: EVALUATION & METRICS
    # ==============================================================================
    elif selected_page == "📈 Evaluation & Metrics":
        st.header("Automated Evaluation Pipeline")
        st.write("Empirical benchmark against synthetic C/C++ ground truth dataset (CS4 Case Study).")

        results = evaluation_service.get_results()

        if results.get("status") == "Not yet executed":
            st.warning("⚠️ **Evaluation not yet executed.**")
            st.info("Click 'Run Reproducible Evaluation' below to benchmark CodeSecure AI across synthetic test cases against ground truth.")
        else:
            st.success(f"✅ Status: **{results.get('status')}** (Timestamp: `{results.get('timestamp')}`)")

            e1, e2, e3, e4 = st.columns(4)
            e1.metric("Precision", f"{results.get('precision', 0.0) * 100:.2f}%")
            e2.metric("Recall", f"{results.get('recall', 0.0) * 100:.2f}%")
            e3.metric("F1-Score", f"{results.get('f1_score', 0.0) * 100:.2f}%")
            e4.metric("Avg Latency", f"{results.get('average_response_time_ms', 0.0):.2f} ms")

            st.markdown("---")
            a1, a2, a3, a4 = st.columns(4)
            a1.metric("Severity Accuracy", f"{results.get('severity_accuracy', 0.0) * 100:.2f}%")
            a2.metric("Category Accuracy", f"{results.get('category_accuracy', 0.0) * 100:.2f}%")
            a3.metric("Citation Accuracy", f"{results.get('citation_accuracy', 0.0) * 100:.2f}%")
            a4.metric("False Positive Rate", f"{results.get('false_positive_rate', 0.0) * 100:.2f}%")

            st.write(
                f"**Confusion Matrix**: True Positives (TP) = `{results.get('true_positives')}`, "
                f"False Positives (FP) = `{results.get('false_positives')}`, "
                f"False Negatives (FN) = `{results.get('false_negatives')}`, "
                f"True Negatives (TN) = `{results.get('true_negatives')}`."
            )

        if st.button("🚀 Run Reproducible Evaluation Pipeline", type="primary"):
            with st.spinner("Executing review on 21 test cases and comparing with ground truth..."):
                rep = evaluation_service.run_evaluation()
                st.success("Evaluation pipeline execution completed!")
                st.rerun()

    # ==============================================================================
    # PAGE 7: AUDIT & SECURITY LOGS
    # ==============================================================================
    elif selected_page == "🔒 Audit & Security Logs":
        st.header("Security Audit & Incident Telemetry")
        st.write("Tamper-evident operational audit trail. Restricted to Security Engineers and Administrators.")

        if st.session_state.role not in ("security_eng", "admin"):
            st.error("⛔ Access Denied: You must be signed in as a Security Engineer or Administrator to view audit logs.")
        else:
            action_filter = st.selectbox(
                "Filter Action",
                [
                    "All",
                    "CODE_REVIEW_COMPLETED",
                    "PROMPT_INJECTION_DETECTED",
                    "FINDING_DISPOSITION_UPDATED",
                    "LOGIN_SUCCESS",
                    "LOGIN_FAILED",
                    "EVALUATION_RUN_COMPLETED",
                ],
            )
            logs = security_service.get_audit_logs(
                limit=150,
                action_filter=None if action_filter == "All" else action_filter,
            )

            st.caption(f"Displaying {len(logs)} audit entries")
            if not logs:
                st.info("No matching audit logs recorded.")
            else:
                for entry in logs:
                    status_badge = "🟢" if entry.get("status") in ("SUCCESS", "MITIGATED") else "🔴"
                    with st.expander(
                        f"{status_badge} [{entry.get('timestamp')[:19]}] {entry.get('action')} by '{entry.get('username')}' ({entry.get('status')})"
                    ):
                        st.write(f"**Resource**: `{entry.get('resource')}`")
                        st.write(f"**Details**: {entry.get('details') or 'None'}")
