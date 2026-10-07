# Synthetic educational knowledge base created for academic demonstration.

# Guideline: KB-SEC-004 — Hardcoded Credentials & State Safety Invariants
**Category**: Security  
**Topic**: Credential & State Safety  
**Citation Code**: KB-SEC-004  
**Severity Default**: High  

## 1. Principle
Source code must never embed hardcoded authentication tokens, API keys, passwords, or cryptographic private keys. In addition, state machines controlling safety-critical hardware must validate transition preconditions to prevent invalid states.

## 2. Vulnerability Pattern
Embedding static secrets in source code:
```cpp
bool authenticateDiagnosticChannel(const char* provided_pin) {
    // VIOLATION: Hardcoded authentication secret in plain text
    const char* HARDCODED_PIN = "ADMIN_DEBUG_TOKEN_12345";
    return strcmp(provided_pin, HARDCODED_PIN) == 0;
}
```

## 3. Remediation & Defensive Rule
- Load secrets dynamically from secure hardware key stores, environment variables, or encrypted configuration storage.
- Never commit private tokens to version control.
- Validate state machine transitions against an allowed transition matrix.
```cpp
bool authenticateDiagnosticChannel(const char* provided_pin) {
    const char* expected_pin = getenv("DIAGNOSTIC_PIN_HASH");
    if (expected_pin == nullptr || provided_pin == nullptr) return false;
    // Constant-time comparison
    return secure_compare(provided_pin, expected_pin);
}
```
