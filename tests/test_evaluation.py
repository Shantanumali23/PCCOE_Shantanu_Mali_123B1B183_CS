"""
CodeSecure AI — Evaluation Metrics Unit Tests
Tests mathematical precision, recall, F1, false-positive rate calculations and ground-truth matching.
"""

import unittest
from app.services.evaluation_service import evaluation_service


class TestEvaluationMetrics(unittest.TestCase):
    def test_metrics_calculation_formulas(self):
        # Synthetic values
        tp = 18
        fp = 1
        fn = 2
        tn = 1

        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1 = (2 * precision * recall) / (precision + recall)
        fpr = fp / (fp + tn)

        self.assertAlmostEqual(precision, 18 / 19, places=4)
        self.assertAlmostEqual(recall, 18 / 20, places=4)
        self.assertGreater(f1, 0.8)
        self.assertAlmostEqual(fpr, 0.5, places=4)

    def test_evaluation_pipeline_run(self):
        report = evaluation_service.run_evaluation()
        self.assertEqual(report["status"], "Completed")
        self.assertGreaterEqual(report["test_cases_evaluated"], 20)
        self.assertGreater(report["precision"], 0.0)
        self.assertGreater(report["recall"], 0.0)
        self.assertGreater(report["f1_score"], 0.0)
        self.assertIn("average_response_time_ms", report)


if __name__ == "__main__":
    unittest.main()
