# Synthetic educational knowledge base created for academic demonstration.

# Guideline: KB-INPUT-002 — Boundary Checks & Input Validation
**Category**: Coding Guidelines  
**Topic**: Input Validation  
**Citation Code**: KB-INPUT-002  
**Severity Default**: High  

## 1. Principle
External inputs, network packet lengths, sensor ranges, and user-supplied arguments must never be trusted implicitly. All input parameters must be bounded against both upper and lower valid operational thresholds prior to processing, memory indexing, or arithmetic.

## 2. Vulnerability Pattern
Trusting length fields or indices received from external sources without validating against container bounds:
```cpp
void parsePacket(const uint8_t* buffer, size_t length) {
    // VIOLATION: length not checked against MAX_PACKET_SIZE
    uint8_t payload[64];
    memcpy(payload, buffer, length); // Potential buffer overflow
}
```

## 3. Remediation & Defensive Rule
Enforce strict range validation before using values as indices or copy lengths:
```cpp
void parsePacket(const uint8_t* buffer, size_t length) {
    constexpr size_t MAX_PAYLOAD_SIZE = 64;
    if (buffer == nullptr || length == 0 || length > MAX_PAYLOAD_SIZE) {
        handle_error(ERR_INVALID_PACKET_LENGTH);
        return;
    }
    uint8_t payload[MAX_PAYLOAD_SIZE];
    memcpy(payload, buffer, length);
}
```

## 4. Key Verification Checklist
- Validate minimum and maximum boundaries on all numeric inputs.
- Reject negative lengths when dealing with signed-to-unsigned conversions.
- Fail closed: reject invalid input immediately and avoid partial state mutations.
