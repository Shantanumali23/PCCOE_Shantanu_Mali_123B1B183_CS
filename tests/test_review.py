"""
CodeSecure AI — Review Pipeline Unit Tests
Tests structured finding normalization, JSON extraction, input rejection, and citation validation.
"""

import unittest
from app.schemas import CodeReviewRequest
from app.services.review_service import review_service
from app.utils.json_utils import extract_json_from_llm


class TestReviewPipeline(unittest.TestCase):
    def test_structured_finding_generation(self):
        code = "void processSensor(int* sensor) { int value = sensor[0]; }"
        req = CodeReviewRequest(
            code=code,
            file_name="sensor.cpp",
            review_type="Security Review",
        )
        resp = review_service.review_code(req, username="tester")
        self.assertIsNotNone(resp)
        self.assertGreater(len(resp.findings), 0)

        f = resp.findings[0]
        self.assertEqual(f.category, "Memory Safety")
        self.assertEqual(f.severity, "High")
        self.assertIn("KB-MEM-001", f.citations)
        self.assertTrue(f.confidence > 0.0)

    def test_json_extraction_from_markdown(self):
        llm_raw = (
            "Here is the security review findings report:\n"
            "```json\n"
            "{\n"
            '  "findings": [\n'
            "    {\n"
            '      "id": "F001",\n'
            '      "severity": "High",\n'
            '      "category": "Memory Safety",\n'
            '      "file": "test.cpp",\n'
            '      "issue": "Null pointer",\n'
            '      "recommendation": "Add check",\n'
            '      "confidence": 0.9\n'
            "    }\n"
            "  ]\n"
            "}\n"
            "```\n"
            "End of report."
        )
        parsed = extract_json_from_llm(llm_raw)
        self.assertIsNotNone(parsed)
        self.assertIn("findings", parsed)
        self.assertEqual(len(parsed["findings"]), 1)

    def test_empty_code_rejection(self):
        req = CodeReviewRequest(code="", file_name="empty.cpp")
        with self.assertRaises(ValueError):
            review_service.review_code(req, username="tester")

    def test_unsupported_file_extension(self):
        req = CodeReviewRequest(code="echo hello", file_name="script.sh")
        with self.assertRaises(ValueError):
            review_service.review_code(req, username="tester")


if __name__ == "__main__":
    unittest.main()
