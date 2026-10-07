# Synthetic educational knowledge base created for academic demonstration.

# Guideline: KB-MISRA-003 — Type Safety & Signed/Unsigned Conversions
**Category**: MISRA-Oriented Guidance  
**Topic**: Type Safety  
**Citation Code**: KB-MISRA-003  
**Severity Default**: High  

## 1. Educational Overview
*Educational summary inspired by automotive/embedded defensive engineering practices. Not an official MISRA standard publication.*

Implicit conversions between signed and unsigned integer types can lead to subtle vulnerabilities. A negative signed integer, when implicitly converted to an unsigned integer, wraps around to an extremely large positive value, which frequently bypasses validation bounds or triggers buffer overflows.

## 2. Guideline Rules
1. Comparisons between signed and unsigned types must be prohibited or explicitly cast with range validation.
2. Standard fixed-width types from `<cstdint>` (e.g., `uint32_t`, `int16_t`) should be used rather than fundamental types (`int`, `short`, `long`) to guarantee predictable word lengths across architectures.
3. Narrowing conversions (e.g., `int32_t` to `int8_t`) must be explicitly guarded against truncation.

## 3. Vulnerability Pattern
Comparing signed length with unsigned buffer limit:
```cpp
bool validateInputLength(int signed_len, size_t max_allowed) {
    // VIOLATION: if signed_len is negative (-1), comparison against unsigned promotes signed_len to size_t max!
    if (signed_len > max_allowed) {
        return false;
    }
    return true; // Returns true for negative numbers!
}
```

## 4. Remediation
```cpp
bool validateInputLength(int signed_len, size_t max_allowed) {
    if (signed_len < 0) {
        return false; // Reject negative inputs explicitly
    }
    if (static_cast<size_t>(signed_len) > max_allowed) {
        return false;
    }
    return true;
}
```
