# CodeSecure AI — Security Review Prompt

You are tasked with executing a rigorous security code audit on the provided C/C++ code.

- Target File: {{file_name}}
- Retrieved Knowledge Base Guidelines (Citations):
{{rag_context}}

- Source Code Under Analysis:
{{code_data}}

### Focus Areas:
1. Memory Safety: Null pointer dereferences, use-after-free, double free, heap/stack buffer overflows.
2. Arithmetic Safety: Integer overflow, wraparound, signed/unsigned comparisons.
3. Resource Management: Leaked file handles, memory allocations without corresponding free.
4. Injection & Secrets: Hardcoded credentials, debug flags, unvalidated external strings.

### Output Requirement:
Respond with a single JSON object conforming to the schema below.
DO NOT wrap your response with conversational preambles or postscripts.
Every finding MUST cite relevant retrieved guidelines where applicable (e.g., "KB-SEC-001", "KB-MEM-001").

```json
{
  "findings": [
    {
      "id": "F001",
      "severity": "Critical|High|Medium|Low|Informational",
      "category": "Buffer Safety|Memory Safety|Integer Safety|Input Validation|Resource Management|Credential Safety",
      "file": "{{file_name}}",
      "function": "functionName",
      "line": 12,
      "issue": "Specific vulnerability description",
      "evidence": "Exact code line or statement illustrating the issue",
      "root_cause": "Underlying design flaw or missing defensive check",
      "recommendation": "Concrete refactored code or defensive measure",
      "rule": "KB-SEC-001",
      "confidence": 0.95,
      "status": "Open",
      "citations": ["KB-SEC-001"]
    }
  ]
}
```
