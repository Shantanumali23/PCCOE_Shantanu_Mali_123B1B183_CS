"""
CodeSecure AI — FastAPI Endpoints Integration Tests
Tests /health, /auth/login, /reviews/code, /findings, and RBAC endpoint protection.
"""

import unittest
from app.main import app
from app.security.authentication import create_access_token

try:
    from fastapi.testclient import TestClient
    TEST_CLIENT_AVAILABLE = True
except ImportError:
    TEST_CLIENT_AVAILABLE = False


class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        if TEST_CLIENT_AVAILABLE:
            self.client = TestClient(app)
        else:
            self.client = None

        self.dev_token = create_access_token({"sub": "developer", "role": "developer", "id": 3})
        self.rev_token = create_access_token({"sub": "reviewer", "role": "reviewer", "id": 2})
        self.admin_token = create_access_token({"sub": "admin", "role": "admin", "id": 1})

    def test_health_check(self):
        if not self.client:
            self.skipTest("TestClient not installed")
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("llm_service", data)
        self.assertIn("rag_service", data)

    def test_auth_login_valid(self):
        if not self.client:
            self.skipTest("TestClient not installed")
        payload = {"username": "developer", "password": "Dev@CodeSecure2026"}
        response = self.client.post("/auth/login", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["role"], "developer")

    def test_auth_login_invalid(self):
        if not self.client:
            self.skipTest("TestClient not installed")
        payload = {"username": "developer", "password": "WrongPassword"}
        response = self.client.post("/auth/login", json=payload)
        self.assertEqual(response.status_code, 401)

    def test_code_review_api(self):
        if not self.client:
            self.skipTest("TestClient not installed")
        headers = {"Authorization": f"Bearer {self.dev_token}"}
        payload = {
            "code": "void processSensor(int* sensor) { int val = sensor[0]; }",
            "file_name": "api_test.cpp",
            "review_type": "Security Review",
        }
        response = self.client.post("/reviews/code", json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("findings", data)
        self.assertGreater(len(data["findings"]), 0)

    def test_audit_logs_rbac_protection(self):
        if not self.client:
            self.skipTest("TestClient not installed")
        # Developer is NOT authorized to view audit logs (HTTP 403)
        dev_headers = {"Authorization": f"Bearer {self.dev_token}"}
        resp_dev = self.client.get("/audit-logs", headers=dev_headers)
        self.assertEqual(resp_dev.status_code, 403)

        # Admin IS authorized to view audit logs (HTTP 200)
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        resp_admin = self.client.get("/audit-logs", headers=admin_headers)
        self.assertEqual(resp_admin.status_code, 200)


if __name__ == "__main__":
    unittest.main()
