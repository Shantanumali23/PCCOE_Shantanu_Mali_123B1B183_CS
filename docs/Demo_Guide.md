# CodeSecure AI — Step-by-Step Live Demo Guide

This guide walks through the complete end-to-end demonstration sequence for project evaluation, viva, and technical review.

---

### Step 1: User Authentication & Role Selection
1. Launch the Streamlit application (`http://localhost:8501`).
2. In the left sidebar, log in using the demo account:
   - **Username**: `developer`
   - **Password**: `Dev@CodeSecure2026`
3. Notice that the role is recognized as `developer`.

---

### Step 2: Open Code Review Workspace
1. In the sidebar, select **"🔍 Code Review"**.
2. Notice the warning banner: *"AI-assisted analysis — human review required. Does not claim certified MISRA compliance."*

---

### Step 3: Select a Vulnerable C++ Sample
1. From the **"Load Synthetic Sample Code"** dropdown, select `tc01_null_pointer.cpp`.
2. Observe the code snippet:
   ```cpp
   void processSensor(int* sensor) {
       int value = sensor[0]; // Defect: dereferenced without nullptr check
   }
   ```

---

### Step 4: Run Security Review
1. Set **Review Type** to `Security Review`.
2. Click **"🚀 Run Privacy-Preserving Review"**.
3. Observe the loading spinner while local RAG retrieval and analysis execute.

---

### Step 5: Inspect RAG Retrieval
1. Expand the **"📚 Retrieved RAG Grounding Context"** accordion at the bottom.
2. View retrieved chunks for `KB-MEM-001` (Memory Safety & Pointer Verification) with similarity scores and principles.

---

### Step 6: Review Structured Findings
1. Examine the generated finding:
   - **Severity**: `High`
   - **Category**: `Memory Safety`
   - **Issue**: `Potential null pointer dereference`
   - **Observed Evidence**: `int value = sensor[0];`
   - **Root Cause Hypothesis**: `Pointer is dereferenced without checking for nullptr or NULL`
   - **Recommendation**: `Validate pointer before dereferencing`
   - **Citations**: `KB-MEM-001`

---

### Step 7: Inspect Citation Details
1. Navigate to **"📚 RAG Knowledge Base"** in the sidebar.
2. Search for `KB-MEM-001` or `null pointer`.
3. View the educational guideline, vulnerability pattern, and defensive remediation idiom.

---

### Step 8: Human-in-the-Loop Reviewer Disposition
1. Log in as a Reviewer:
   - In sidebar, click **Log Out**, then log in with `reviewer` / `Reviewer@CodeSecure2026`.
2. Navigate to **"📝 Findings Management"**.
3. Locate the finding for `sensor.cpp`.
4. In the disposition controls:
   - Change **Status** from `Open` to `Confirmed`.
   - Add Comment: `"Confirmed during sprint review; ticket ENG-402 filed to add defensive check."`
   - Click **Save Disposition**.
5. Observe the status update reflected immediately.

---

### Step 9: Inspect Security Audit Logs
1. Log in as a Security Engineer:
   - Log in with `security_eng` / `SecEng@CodeSecure2026`.
2. Navigate to **"🔒 Audit & Security Logs"**.
3. View recorded events:
   - `CODE_REVIEW_COMPLETED`
   - `FINDING_DISPOSITION_UPDATED`
   - Any `PROMPT_INJECTION_DETECTED` events.
4. Verify that no raw source code or passwords appear in the audit records.

---

### Step 10: Run Reproducible Evaluation Pipeline
1. Navigate to **"📈 Evaluation & Metrics"**.
2. Click **"🚀 Run Reproducible Evaluation Pipeline"**.
3. Observe measured metrics across all 21 test cases:
   - **Precision**: ~100%
   - **Recall**: ~85%
   - **F1-Score**: ~91.89%
   - **Average Latency**: ~1-2 ms
   - Confusion matrix counts (TP, FP, FN, TN).
4. Review the generated `evaluation/results/evaluation_report.json`.
