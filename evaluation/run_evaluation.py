"""
CodeSecure AI — Automated Evaluation Runner
Executes evaluation against synthetic ground truth dataset and reports actual measured metrics.
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.evaluation_service import evaluation_service
from app.utils.logging_utils import get_logger

logger = get_logger("run_evaluation_script")


def main():
    print("=" * 70)
    print("  CodeSecure AI — Evaluation Pipeline Runner")
    print("  Privacy-Preserving Secure Code Debugging and Review")
    print("=" * 70)
    print("\n[+] Initiating reproducible evaluation across synthetic test cases...")

    report = evaluation_service.run_evaluation()

    print("\n" + "=" * 70)
    print("  MEASURED EVALUATION RESULTS")
    print("=" * 70)
    print(f"  Test Cases Evaluated  : {report['test_cases_evaluated']}")
    print(f"  True Positives (TP)   : {report['true_positives']}")
    print(f"  False Positives (FP)  : {report['false_positives']}")
    print(f"  False Negatives (FN)  : {report['false_negatives']}")
    print(f"  True Negatives (TN)   : {report['true_negatives']}")
    print("-" * 70)
    print(f"  Precision             : {report['precision'] * 100:.2f}%")
    print(f"  Recall                : {report['recall'] * 100:.2f}%")
    print(f"  F1-Score              : {report['f1_score'] * 100:.2f}%")
    print(f"  Severity Accuracy     : {report['severity_accuracy'] * 100:.2f}%")
    print(f"  Category Accuracy     : {report['category_accuracy'] * 100:.2f}%")
    print(f"  Citation Accuracy     : {report['citation_accuracy'] * 100:.2f}%")
    print(f"  False Positive Rate   : {report['false_positive_rate'] * 100:.2f}%")
    print(f"  Average Latency       : {report['average_response_time_ms']:.2f} ms")
    print("=" * 70)
    print(f"\n[+] Results persisted to: evaluation/results/evaluation_report.json")
    print(f"[+] Case predictions saved to: evaluation/predictions.json\n")


if __name__ == "__main__":
    main()
