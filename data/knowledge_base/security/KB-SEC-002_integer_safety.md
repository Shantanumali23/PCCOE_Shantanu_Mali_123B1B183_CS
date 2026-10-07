# Synthetic educational knowledge base created for academic demonstration.

# Guideline: KB-SEC-002 — Integer Overflow & Arithmetic Wraparound
**Category**: Security  
**Topic**: Integer Safety  
**Citation Code**: KB-SEC-002  
**Severity Default**: High  

## 1. Principle
Arithmetic operations on fixed-width integer types can overflow or underflow when the result exceeds representable limits. In signed arithmetic, overflow is undefined behavior; in unsigned arithmetic, wraparound occurs silently. When resulting integers govern memory allocations or copy sizes, severe vulnerabilities arise.

## 2. Vulnerability Pattern
Allocating buffer memory based on an unbounded addition of dimensions:
```cpp
void* allocateMatrix(size_t width, size_t height) {
    // VIOLATION: width * height can overflow size_t, allocating a tiny buffer
    size_t total_size = width * height; 
    return malloc(total_size);
}
```

## 3. Remediation & Defensive Rule
Verify arithmetic bounds prior to execution:
```cpp
void* allocateMatrix(size_t width, size_t height) {
    if (width != 0 && height > SIZE_MAX / width) {
        // Overflow detected
        return nullptr;
    }
    size_t total_size = width * height;
    return malloc(total_size);
}
```

## 4. Key Verification Checklist
- Check addition against `MAX - val`.
- Check multiplication against `MAX / val`.
- Use compiler built-ins (e.g., `__builtin_add_overflow`, `__builtin_mul_overflow`) where supported.
