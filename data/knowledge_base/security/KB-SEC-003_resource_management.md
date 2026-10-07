# Synthetic educational knowledge base created for academic demonstration.

# Guideline: KB-SEC-003 — Resource Management, Use-After-Free & Double Free
**Category**: Security  
**Topic**: Resource Management  
**Citation Code**: KB-SEC-003  
**Severity Default**: Critical  

## 1. Principle
Dynamically allocated memory and operating system handles (files, sockets, mutexes) must have well-defined ownership lifetimes. Accessing memory after it has been freed (`use-after-free`), freeing memory more than once (`double free`), or failing to free memory before all references are lost (`memory leak`) are critical defects.

## 2. Vulnerability Pattern
Accessing pointer after release:
```cpp
void handleSession() {
    char* token = (char*)malloc(32);
    free(token);
    // VIOLATION: Use-after-free
    logToken(token); 
}
```
Double free vulnerability:
```cpp
void cleanup(char* ptr) {
    free(ptr);
    // VIOLATION: Double free if called twice or pointer not nulled
    free(ptr); 
}
```

## 3. Remediation & Defensive Rule
Apply Resource Acquisition Is Initialization (RAII), use smart pointers, or explicitly null pointers after freeing:
```cpp
void cleanup(char*& ptr) {
    if (ptr != nullptr) {
        free(ptr);
        ptr = nullptr; // Mitigates double free and dangling dereference
    }
}
```

## 4. Key Verification Checklist
- Set pointers to `nullptr` immediately after `free` or `delete`.
- Ensure all allocation error return paths call appropriate deallocation functions.
- In modern C++, utilize `std::unique_ptr` and standard containers.
