# Synthetic educational knowledge base created for academic demonstration.

# Guideline: KB-SEC-001 — Buffer Safety & Bounded String Operations
**Category**: Security  
**Topic**: Buffer Safety  
**Citation Code**: KB-SEC-001  
**Severity Default**: Critical  

## 1. Principle
Unchecked array indexing and unsafe string functions (`strcpy`, `strcat`, `sprintf`, `gets`) write past buffer boundaries, corrupting the call stack or adjacent heap metadata. All string and memory manipulations must use bounded alternatives with explicit length specifications.

## 2. Vulnerability Pattern
Copying unbounded source strings into fixed destination buffers:
```cpp
void copyUserTag(const char* input) {
    char buffer[16];
    // VIOLATION: strcpy does not check input length against 16 bytes
    strcpy(buffer, input); 
}
```

## 3. Remediation & Defensive Rule
Use bounded functions and guarantee null-termination, or utilize safe modern C++ containers (`std::string`, `std::string_view`, `std::array`):
```cpp
void copyUserTag(const char* input) {
    if (input == nullptr) return;
    char buffer[16];
    // Use snprintf or strncpy with explicit null termination
    snprintf(buffer, sizeof(buffer), "%s", input);
    buffer[sizeof(buffer) - 1] = '\0';
}
```

## 4. Key Verification Checklist
- Replace `strcpy` with `strncpy` or `snprintf`.
- Check off-by-one errors on null terminator space requirements.
- Validate array indices against container size `size()`.
