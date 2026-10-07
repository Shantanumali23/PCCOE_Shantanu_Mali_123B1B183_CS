"""
CodeSecure AI — Authentication & Authorization Unit Tests
"""

import unittest
from app.security.authentication import create_access_token, hash_password, verify_access_token, verify_password
from app.security.authorization import Role, Permission, has_permission, is_role_authorized_for_repo


class TestAuthentication(unittest.TestCase):
    def test_password_hashing_and_verification(self):
        password = "SecurePassword@123"
        hashed = hash_password(password)
        self.assertNotEqual(password, hashed)
        self.assertTrue(hashed.startswith("pbkdf2_sha256$"))
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))

    def test_jwt_token_generation_and_validation(self):
        payload = {"sub": "developer_test", "role": "developer"}
        token = create_access_token(payload)
        self.assertIsInstance(token, str)
        self.assertEqual(len(token.split(".")), 3)

        decoded = verify_access_token(token)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["sub"], "developer_test")
        self.assertEqual(decoded["role"], "developer")

    def test_tampered_token_rejection(self):
        token = create_access_token({"sub": "admin", "role": "admin"})
        tampered_token = token[:-4] + "xxxx"
        decoded = verify_access_token(tampered_token)
        self.assertIsNone(decoded)

    def test_rbac_permissions(self):
        # Developer has code upload but not disposition or audit view
        self.assertTrue(has_permission(Role.DEVELOPER, Permission.CODE_UPLOAD))
        self.assertFalse(has_permission(Role.DEVELOPER, Permission.FINDINGS_DISPOSITION))
        self.assertFalse(has_permission(Role.DEVELOPER, Permission.AUDIT_VIEW))

        # Reviewer can disposition findings
        self.assertTrue(has_permission(Role.REVIEWER, Permission.FINDINGS_DISPOSITION))
        self.assertFalse(has_permission(Role.REVIEWER, Permission.SYSTEM_CONFIG))

        # Security engineer can view audit logs
        self.assertTrue(has_permission(Role.SECURITY_ENGINEER, Permission.AUDIT_VIEW))

        # Admin has full privileges
        self.assertTrue(has_permission(Role.ADMIN, Permission.PROJECT_MANAGE))
        self.assertTrue(has_permission(Role.ADMIN, Permission.USER_MANAGE))

    def test_repository_authorization(self):
        allowed_roles = "reviewer,security_engineer,admin"
        self.assertTrue(is_role_authorized_for_repo("reviewer", allowed_roles))
        self.assertTrue(is_role_authorized_for_repo("admin", allowed_roles))
        self.assertFalse(is_role_authorized_for_repo("developer", allowed_roles))


if __name__ == "__main__":
    unittest.main()
