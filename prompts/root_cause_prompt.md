# CodeSecure AI — Root Cause Analysis Prompt

You are tasked with isolating the fundamental root cause of an identified software defect.

- Finding Summary: {{finding_summary}}
- Code Excerpt: {{code_excerpt}}
- Relevant Guidelines: {{rag_context}}

### Analysis Guidelines:
1. Distinguish proximate failure symptom (e.g., process crash, corrupt buffer) from underlying root cause (e.g., absence of length validation at boundary).
2. Trace lifecycle of the implicated variable or memory block.
3. Determine whether the flaw stems from architectural design, specification ambiguity, or implementation omission.
4. Provide a defensive pattern that systematically eliminates the vulnerability class.
