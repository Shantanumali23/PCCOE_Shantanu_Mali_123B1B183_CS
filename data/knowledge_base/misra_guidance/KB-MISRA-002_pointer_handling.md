# Synthetic educational knowledge base created for academic demonstration.

# Guideline: KB-MISRA-002 — Pointer Arithmetic & Dangling Pointer Prevention
**Category**: MISRA-Oriented Guidance  
**Topic**: Pointer Handling  
**Citation Code**: KB-MISRA-002  
**Severity Default**: High  

## 1. Educational Overview
*Educational summary inspired by automotive/embedded defensive engineering practices. Not an official MISRA standard publication.*

Pointer arithmetic is a frequent source of out-of-bounds reads/writes, buffer underflows, and undefined behavior. Pointers must never be indexed or incremented past the address of the one-past-the-end element of an array.

## 2. Guideline Rules
1. Pointer arithmetic should be restricted to indexing within verified array bounds.
2. Pointers must not be compared across distinct, unrelated memory allocations.
3. Immediately reset deallocated pointers to `nullptr` to prevent dangling references and use-after-free conditions.

## 3. Vulnerability Pattern
Unchecked pointer stepping over a buffer:
```cpp
void stepBuffer(int* ptr, size_t count) {
    // VIOLATION: incrementing pointer without validating buffer capacity
    for(size_t i = 0; i < count; ++i) {
        *ptr++ = 0;
    }
}
```

## 4. Remediation
```cpp
void stepBuffer(int* buffer, size_t buffer_len, size_t count) {
    if (buffer == nullptr || count > buffer_len) {
        return;
    }
    for(size_t i = 0; i < count; ++i) {
        buffer[i] = 0;
    }
}
```
