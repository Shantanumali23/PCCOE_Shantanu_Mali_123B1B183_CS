# CodeSecure AI — Threat Model & Security Posture

## 1. Overview
This threat model assesses the threat vectors confronting **CodeSecure AI** under the STRIDE methodology and documents corresponding architectural mitigations.

---

## 2. Threat Analysis & Mitigations Matrix

| Threat Category | Threat Scenario | Impact | CodeSecure AI Mitigation |
|---|---|---|---|
| **Information Disclosure** | Proprietary source code transmitted to external cloud APIs | High | **Host-Isolated AI**: Default architecture runs local Ollama LLMs on `localhost`. Cloud AI APIs are disabled by default. |
| **Tampering** | Prompt Injection via embedded commentary (e.g. `/* Ignore previous instructions */`) | High | **Layered Injection Defense**: Regex signature detection, untrusted data containers (`<UNTRUSTED_CODE_DATA>`), and delimiter escaping. |
| **Elevation of Privilege** | Developer accesses security audit logs or modifies findings | Medium | **Role-Based Access Control (RBAC)**: Enforced via `has_permission()` checks on all API endpoints and UI components. |
| **Information Disclosure** | Path traversal attempting to read `/etc/passwd` or outside projects | Critical | **Path Sandboxing**: Resolved paths validated against allowed directory root using `os.path.commonpath()`. Null bytes blocked. |
| **Denial of Service** | Uploading massive binary files to overwhelm memory/inference | High | **Payload Guardrails**: Maximum upload size capped at 2 MB (`MAX_UPLOAD_SIZE_MB`). Strict file extension whitelist. |
| **Repudiation** | User changes finding status without accountability | Medium | **Tamper-Evident Audit Logs**: All state transitions record `user_id`, `username`, `action`, `timestamp`, and `status`. |
| **Information Disclosure** | Passwords, tokens, or confidential source code leaked in log files | High | **Redacting Logging Formatter**: Automatic regex scrubbers redact secrets, bearer tokens, and credentials in stdout/file logs. |
| **Remote Code Execution** | Malicious C++ payload compiled or executed by host server | Critical | **No Arbitrary Code Execution**: Submitted source code is analyzed strictly through static AI and AST/regex patterns; code is never compiled or executed. |
| **Integrity Loss** | Model hallucination produces false safety assurances | High | **Human-in-the-Loop Governance**: AI findings are explicitly marked as unverified until confirmed by a human reviewer. RAG citations require guideline grounding. |
