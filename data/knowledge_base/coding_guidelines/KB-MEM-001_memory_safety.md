# Synthetic educational knowledge base created for academic demonstration.

# Guideline: KB-MEM-001 — Memory Safety & Pointer Verification
**Category**: Coding Guidelines  
**Topic**: Memory Safety  
**Citation Code**: KB-MEM-001  
**Severity Default**: High  

## 1. Principle
In C and C++ embedded and safety-critical software, dynamic or passed memory pointers must be validated for `nullptr` / `NULL` before any dereference, index operation, or member access. Dereferencing an unvalidated pointer triggers undefined behavior, segmentation faults, or exploitable memory corruption.

## 2. Vulnerability Pattern
Accessing an element of an array or struct through a raw pointer without validating whether the pointer is null:
```cpp
void processSensor(int* sensor) {
    // VIOLATION: sensor dereferenced without prior null check
    int value = sensor[0]; 
}
```

## 3. Remediation & Defensive Rule
Always perform early validation and defensive exit or assertion:
```cpp
void processSensor(const int* sensor) {
    if (sensor == nullptr) {
        // Defensive error handling / fallback
        report_error("Invalid sensor pointer");
        return;
    }
    int value = sensor[0];
}
```

## 4. Key Verification Checklist
- Check all incoming pointer arguments at function entry.
- Verify return values of allocation functions (`malloc`, `calloc`, `new (std::nothrow)`).
- Prefer smart pointers (`std::unique_ptr`, `std::shared_ptr`) or references where dynamic allocation is required in modern C++.
