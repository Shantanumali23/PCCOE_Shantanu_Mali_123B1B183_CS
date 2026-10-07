# CodeSecure AI — Limitations & Constraints

## 1. Important Academic & Operational Disclaimers
1. **Not Certified MISRA Compliance**:
   - CodeSecure AI provides **MISRA-oriented educational guidance** and defensive programming heuristics.
   - It is **NOT** a certified MISRA checker, does NOT guarantee compliance with official MISRA C:2012 or MISRA C++:2023 standards, and does NOT replace ISO 26262 qualified static analysis tools (e.g., Coverity, Polyspace, Klocwork).
2. **AI-Assisted Tooling, Not Autonomous Authority**:
   - AI outputs must never be treated as autonomous code approvals.
   - All findings require explicit human review and disposition before altering codebases.

---

## 2. Technical Limitations
1. **Model Parameter Trade-offs**:
   - When running on resource-constrained student laptops, smaller quantized models (e.g. 1.5B or 7B Q4) have lower context retention and may exhibit occasional hallucinations or miss complex multi-file inter-procedural defects.
2. **Knowledge Base Scope**:
   - RAG grounding relies on synthetic educational guidelines created for academic demonstration. While representative of common automotive/embedded patterns, they do not encompass the full breadth of all proprietary standards.
3. **No Dynamic Execution / Fuzzing**:
   - The platform strictly performs static pattern and semantic analysis. It does not dynamically execute code, run symbolic execution engines, or fuzz binaries.
4. **Single-File Scope**:
   - Analysis is currently optimized for single files and moderate translation units; complex cross-translation-unit whole-program data flow tracking is outside current scope.
