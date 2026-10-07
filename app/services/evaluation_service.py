"""
CodeSecure AI — Evaluation Service
Executes automated, reproducible evaluation against ground truth test cases.
Calculates Precision, Recall, F1, Severity Accuracy, Citation Accuracy, False-Positive Rate,
and Latency. Returns "Not yet executed" until actually run.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.schemas import CodeReviewRequest
from app.services.review_service import review_service
from app.utils.logging_utils import get_logger

logger = get_logger("evaluation_service")


class EvaluationService:
    """Manages evaluation lifecycle, ground truth matching, and metrics calculation."""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.ground_truth_path = self.base_dir / "evaluation" / "ground_truth.json"
        self.code_samples_dir = self.base_dir / "data" / "code_samples"
        self.results_dir = self.base_dir / "evaluation" / "results"
        self.report_path = self.results_dir / "evaluation_report.json"
        self.predictions_path = self.base_dir / "evaluation" / "predictions.json"

    def get_results(self) -> Dict[str, Any]:
        """
        Retrieves the latest executed evaluation report.
        If evaluation has not yet been executed, returns an explicit unexecuted status.
        """
        if not self.report_path.exists():
            return {
                "status": "Not yet executed",
                "message": "Evaluation has not yet been executed. Run evaluation via API, CLI, or UI to generate measured metrics.",
                "test_cases_evaluated": 0,
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0,
                "severity_accuracy": 0.0,
                "category_accuracy": 0.0,
                "citation_accuracy": 0.0,
                "false_positive_rate": 0.0,
                "average_response_time_ms": 0.0,
                "timestamp": None,
            }

        try:
            with open(self.report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception as e:
            logger.error(f"Error loading evaluation report: {e}")
            return {"status": "Error loading report", "error": str(e)}

    def run_evaluation(self) -> Dict[str, Any]:
        """
        Executes end-to-end evaluation:
        1. Loads ground truth dataset.
        2. Executes CodeSecure AI review on each sample.
        3. Measures latency.
        4. Compares predictions with ground truth.
        5. Computes Precision, Recall, F1, and subordinate accuracies.
        6. Persists measured results.
        """
        if not self.ground_truth_path.exists():
            raise FileNotFoundError(f"Ground truth dataset missing at {self.ground_truth_path}")

        with open(self.ground_truth_path, "r", encoding="utf-8") as f:
            ground_truth_cases = json.load(f)

        self.results_dir.mkdir(parents=True, exist_ok=True)

        total_cases = len(ground_truth_cases)
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        true_negatives = 0

        severity_matches = 0
        category_matches = 0
        citation_matches = 0

        eval_predictions = []
        total_latency_ms = 0.0

        logger.info(f"Starting evaluation across {total_cases} test cases...")

        for case in ground_truth_cases:
            sample_id = case.get("sample_id", "")
            file_name = case.get("file", "")
            expected_category = case.get("category", "")
            expected_severity = case.get("severity", "")
            expected_rule = case.get("expected_rule", "")
            is_benign = (expected_category == "Safe Equivalent")

            # Load code
            code_path = self.code_samples_dir / file_name
            if not code_path.exists():
                logger.warning(f"Test case file missing: {code_path}")
                continue

            code_text = code_path.read_text(encoding="utf-8", errors="replace")

            # Execute review and measure response time
            start_t = time.perf_counter()
            review_req = CodeReviewRequest(
                code=code_text,
                file_name=file_name,
                review_type="Security Review",
            )
            response = review_service.review_code(review_req, username="evaluator")
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            total_latency_ms += elapsed_ms

            findings = response.findings
            # Filter out purely informational or safe confirmations for defect scoring
            defect_findings = [f for f in findings if f.severity != "Informational"]

            case_prediction = {
                "sample_id": sample_id,
                "file": file_name,
                "latency_ms": round(elapsed_ms, 2),
                "findings_count": len(findings),
                "predicted_findings": [f.model_dump() if hasattr(f, "model_dump") else f.__dict__ for f in findings],
            }
            eval_predictions.append(case_prediction)

            if is_benign:
                if len(defect_findings) == 0:
                    true_negatives += 1
                else:
                    false_positives += 1
            else:
                if len(defect_findings) > 0:
                    true_positives += 1
                    # Evaluate top matching finding
                    best_match = defect_findings[0]
                    if best_match.severity.lower() == expected_severity.lower():
                        severity_matches += 1
                    if (
                        best_match.category.lower() in expected_category.lower()
                        or expected_category.lower() in best_match.category.lower()
                    ):
                        category_matches += 1
                    if expected_rule in best_match.citations or best_match.rule == expected_rule:
                        citation_matches += 1
                else:
                    false_negatives += 1

        # Calculate exact metrics
        precision = (
            true_positives / (true_positives + false_positives)
            if (true_positives + false_positives) > 0
            else 0.0
        )
        recall = (
            true_positives / (true_positives + false_negatives)
            if (true_positives + false_negatives) > 0
            else 0.0
        )
        f1_score = (
            (2 * precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        fpr = (
            false_positives / (false_positives + true_negatives)
            if (false_positives + true_negatives) > 0
            else 0.0
        )

        vulnerable_count = total_cases - 1  # Excluding the safe equivalent
        sev_acc = (severity_matches / vulnerable_count) if vulnerable_count > 0 else 0.0
        cat_acc = (category_matches / vulnerable_count) if vulnerable_count > 0 else 0.0
        cite_acc = (citation_matches / vulnerable_count) if vulnerable_count > 0 else 0.0
        avg_latency = total_latency_ms / total_cases if total_cases > 0 else 0.0

        report = {
            "status": "Completed",
            "test_cases_evaluated": total_cases,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "true_negatives": true_negatives,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1_score, 4),
            "severity_accuracy": round(sev_acc, 4),
            "category_accuracy": round(cat_acc, 4),
            "citation_accuracy": round(cite_acc, 4),
            "false_positive_rate": round(fpr, 4),
            "average_response_time_ms": round(avg_latency, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Persist report and predictions
        with open(self.report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        with open(self.predictions_path, "w", encoding="utf-8") as f:
            json.dump(eval_predictions, f, indent=2)

        logger.info(f"Evaluation report generated successfully: F1={report['f1_score']}")
        return report


# Singleton instance
evaluation_service = EvaluationService()
