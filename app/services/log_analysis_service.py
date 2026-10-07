"""
CodeSecure AI — Compiler & Log Analysis Service
Parses compiler diagnostics (GCC/Clang/MSVC), static analysis reports (Cppcheck),
and runtime memory sanitizer traces (Valgrind/AddressSanitizer) with RAG grounding.
"""

import re
from typing import Any, Dict, List, Optional
from app.schemas import LogAnalysisRequest, LogAnalysisResponse, LogIssueItem
from app.security.input_validation import validate_log_content
from app.security.prompt_injection import analyze_and_sanitize
from app.services.rag_service import rag_service
from app.services.security_service import security_service
from app.utils.logging_utils import get_logger

logger = get_logger("log_analysis_service")


class LogAnalysisService:
    """Extracts structured defects from compiler, static analysis, and runtime traces."""

    def parse_log(
        self,
        request: LogAnalysisRequest,
        user_id: Optional[int] = None,
        username: Optional[str] = "developer",
    ) -> LogAnalysisResponse:
        """Parses log content into structured issues grounded by RAG knowledge base."""
        # 1. Input Validation
        is_valid, err_msg = validate_log_content(request.log_content)
        if not is_valid:
            raise ValueError(err_msg)

        # 2. Prompt injection defense
        sec_report = analyze_and_sanitize(request.log_content, data_type="LOG")

        raw_text = request.log_content
        issues: List[LogIssueItem] = []
        cited_guidelines = set()

        # Pattern 1: GCC / Clang compiler diagnostics:
        # e.g.: filename.cpp:12:5: error/warning: message [-Wflag]
        gcc_pattern = re.compile(
            r"([a-zA-Z0-9_\-\.\/]+\.(?:cpp|c|h|hpp|cc)):(\d+):(?:\d+:)?\s*(error|warning|fatal error):\s*([^\n\[]+)(?:\[([a-zA-Z0-9_\-]+)\])?",
            re.IGNORECASE,
        )
        for match in gcc_pattern.finditer(raw_text):
            filename, line_str, sev, msg, flag = match.groups()
            line = int(line_str)
            severity = "Error" if "error" in sev.lower() else "Warning"
            clean_msg = msg.strip()
            err_code = flag or sev.upper()

            cause, step, guideline = self._infer_root_cause_and_step(clean_msg, err_code)
            if guideline:
                cited_guidelines.add(guideline)

            issues.append(
                LogIssueItem(
                    file=filename,
                    line=line,
                    error_code=err_code,
                    severity=severity,
                    message=clean_msg,
                    probable_cause=cause,
                    suggested_step=step,
                    relevant_guideline=guideline,
                )
            )

        # Pattern 2: Cppcheck static analysis:
        # e.g.: [filename.cpp:12]: (error/warning) message
        cppcheck_pattern = re.compile(
            r"\[([a-zA-Z0-9_\-\.\/]+\.(?:cpp|c|h|hpp|cc)):(\d+)\]:\s*\((error|warning)\)\s*([^\n]+)",
            re.IGNORECASE,
        )
        for match in cppcheck_pattern.finditer(raw_text):
            filename, line_str, sev, msg = match.groups()
            line = int(line_str)
            severity = "Error" if "error" in sev.lower() else "Warning"
            clean_msg = msg.strip()

            cause, step, guideline = self._infer_root_cause_and_step(clean_msg, "CPPCHECK")
            if guideline:
                cited_guidelines.add(guideline)

            issues.append(
                LogIssueItem(
                    file=filename,
                    line=line,
                    error_code="CPPCHECK_RULE",
                    severity=severity,
                    message=clean_msg,
                    probable_cause=cause,
                    suggested_step=step,
                    relevant_guideline=guideline,
                )
            )

        # Pattern 3: AddressSanitizer (ASan) runtime crashes:
        asan_pattern = re.compile(
            r"ERROR:\s*AddressSanitizer:\s*([a-zA-Z0-9_\-]+)[^\n]*\s*#0\s*0x[a-f0-9]+\s*in\s*(\w+)\s*([a-zA-Z0-9_\-\.\/]+):(\d+)",
            re.IGNORECASE,
        )
        for match in asan_pattern.finditer(raw_text):
            san_type, func, filename, line_str = match.groups()
            line = int(line_str)
            cause = f"AddressSanitizer trapped runtime memory defect: {san_type} in function {func}"
            step = "Audit pointer lifecycle and array indexing boundaries"
            guideline = "KB-SEC-003" if "free" in san_type.lower() else "KB-SEC-001"
            cited_guidelines.add(guideline)

            issues.append(
                LogIssueItem(
                    file=filename,
                    line=line,
                    error_code=f"ASAN_{san_type.upper()}",
                    severity="Critical",
                    message=f"Runtime Memory Defect: {san_type}",
                    probable_cause=cause,
                    suggested_step=step,
                    relevant_guideline=guideline,
                )
            )

        # Pattern 4: Valgrind memory loss summary
        if "definitely lost:" in raw_text:
            leak_match = re.search(r"definitely lost:\s*([0-9,]+)\s*bytes", raw_text)
            leak_bytes = leak_match.group(1) if leak_match else "unknown"
            cited_guidelines.add("KB-SEC-003")
            issues.append(
                LogIssueItem(
                    file="heap_allocation",
                    line=0,
                    error_code="VALGRIND_LEAK",
                    severity="Error",
                    message=f"Valgrind reports {leak_bytes} bytes definitely lost at process termination",
                    probable_cause="Dynamic memory allocated via malloc/new was never freed before pointer references were lost",
                    suggested_step="Identify allocation trace and insert corresponding free() or adopt RAII smart pointers",
                    relevant_guideline="KB-SEC-003",
                )
            )

        # If no regex patterns matched, provide generalized analysis
        if not issues:
            # Query RAG using first 200 chars of log
            rag_results = rag_service.search(raw_text[:200], top_k=2)
            top_rule = rag_results[0]["citation_code"] if rag_results else "KB-ERR-003"
            cited_guidelines.add(top_rule)

            issues.append(
                LogIssueItem(
                    file="general_log",
                    line=None,
                    error_code="LOG_DIAGNOSTIC",
                    severity="Warning",
                    message="Parsed unstructured diagnostic log",
                    probable_cause="Execution or compilation warning requiring developer inspection",
                    suggested_step="Examine diagnostic output against project coding standards",
                    relevant_guideline=top_rule,
                )
            )

        errors_count = sum(1 for i in issues if i.severity in ("Error", "Critical"))
        warnings_count = sum(1 for i in issues if i.severity == "Warning")

        # Audit log
        security_service.log_event(
            action="LOG_ANALYSIS_COMPLETED",
            resource=request.log_type,
            status="SUCCESS",
            user_id=user_id,
            username=username,
            details=f"TotalIssues={len(issues)}, Errors={errors_count}, Warnings={warnings_count}",
        )

        return LogAnalysisResponse(
            total_issues=len(issues),
            errors=errors_count,
            warnings=warnings_count,
            issues=issues,
            rag_guidelines_cited=sorted(list(cited_guidelines)),
        )

    def _infer_root_cause_and_step(self, message: str, code: str) -> Tuple[str, str, str]:
        """Maps diagnostic error patterns to root cause, remediation, and KB guidelines."""
        msg_lower = message.lower()
        code_lower = (code or "").lower()

        if "null" in msg_lower or "dereference" in msg_lower:
            return (
                "Pointer is dereferenced without prior verification of non-null state",
                "Insert defensive null pointer guard before dereferencing",
                "KB-MEM-001",
            )
        elif "bounds" in msg_lower or "overflow" in msg_lower or "out of bounds" in msg_lower:
            return (
                "Array or buffer index exceeds container capacity",
                "Verify loop bounds and use bounded copy functions",
                "KB-SEC-001",
            )
        elif "uninitialized" in msg_lower or "wuninitialized" in code_lower:
            return (
                "Variable read on a code path prior to explicit assignment",
                "Explicitly initialize variable at its declaration site",
                "KB-MISRA-004",
            )
        elif "sign" in msg_lower or "wsign" in code_lower:
            return (
                "Implicit conversion between signed and unsigned types can distort negative values",
                "Enforce explicit casts and check that signed values are non-negative",
                "KB-MISRA-003",
            )
        elif "leak" in msg_lower:
            return (
                "Allocated heap memory not freed on all termination paths",
                "Ensure free() or delete is invoked on all exit branches",
                "KB-SEC-003",
            )
        elif "free" in msg_lower:
            return (
                "Memory pointer freed more than once or accessed after deallocation",
                "Set pointer to nullptr immediately after deallocation",
                "KB-SEC-003",
            )
        else:
            return (
                "Compiler diagnostic indicating potential deviation from defensive standards",
                "Refactor code to satisfy compiler warning and verify behavior",
                "KB-ERR-003",
            )


# Singleton instance
log_analysis_service = LogAnalysisService()
