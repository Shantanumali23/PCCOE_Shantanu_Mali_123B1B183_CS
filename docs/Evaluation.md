# CodeSecure AI — Evaluation Methodology & Metrics

## 1. Evaluation Purpose
The evaluation subsystem benchmarks the accuracy, reliability, and latency of **CodeSecure AI** against an independently authored ground-truth test suite of 21 synthetic C/C++ test cases spanning critical vulnerability classes.

---

## 2. Evaluation Flow

```text
Ground Truth Dataset (evaluation/ground_truth.json)
                         ↓
Synthetic C++ Test Cases (data/code_samples/tc*.cpp)
                         ↓
CodeSecure AI Pipeline (Validation → Defense → RAG → Review)
                         ↓
Predictions Output (evaluation/predictions.json)
                         ↓
Matching Engine (Category, Severity, Line Proximity, Rule)
                         ↓
Performance Metrics (evaluation/results/evaluation_report.json)
```

---

## 3. Mathematical Metric Definitions

### 3.1 Precision
Measures the proportion of identified defect findings that correspond to genuine vulnerabilities:
$$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}$$

### 3.2 Recall
Measures the proportion of genuine vulnerabilities successfully identified by the platform:
$$\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$$

### 3.3 F1-Score
Harmonic mean balancing precision and recall:
$$\text{F1} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

### 3.4 False Positive Rate (FPR)
Rate at which benign code is incorrectly flagged as defective:
$$\text{FPR} = \frac{\text{FP}}{\text{FP} + \text{TN}}$$

### 3.5 Subordinate Accuracy Metrics
- **Severity Accuracy**: Percentage of true positive findings where the predicted severity matches ground truth.
- **Category Accuracy**: Percentage of true positive findings where the defect category matches ground truth.
- **Citation Accuracy**: Percentage of findings correctly citing the relevant RAG guideline code.
- **Average Latency**: Mean time in milliseconds required to execute the complete review pipeline per file.

---

## 4. Execution Commands
To execute the evaluation pipeline and measure actual results:
```bash
# Via script
python scripts/run_evaluation.py

# Via API
curl -X POST http://localhost:8000/evaluation/run -H "Authorization: Bearer <TOKEN>"

# Via Streamlit
Navigate to "📈 Evaluation & Metrics" page and click "Run Reproducible Evaluation Pipeline"
```
