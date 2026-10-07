# Synthetic educational knowledge base created for academic demonstration.

# Guideline: KB-ERR-003 — Comprehensive Error Handling & Return Code Verification
**Category**: Coding Guidelines  
**Topic**: Error Handling  
**Citation Code**: KB-ERR-003  
**Severity Default**: Medium  

## 1. Principle
Functions returning status codes or error flags must have their return values evaluated by the caller. Ignoring return values leads to silent operational failures, inconsistent state transitions, and downstream fault propagation.

## 2. Vulnerability Pattern
Discarding system call or library return codes:
```cpp
void writeTelemetryLog(const char* data) {
    FILE* fp = fopen("/var/log/telemetry.log", "a");
    // VIOLATION: fp is not checked before writing
    fputs(data, fp);
    fclose(fp);
}
```

## 3. Remediation & Defensive Rule
Verify the return code or pointer immediately upon invocation:
```cpp
bool writeTelemetryLog(const char* data) {
    if (data == nullptr) return false;
    FILE* fp = fopen("/var/log/telemetry.log", "a");
    if (fp == nullptr) {
        log_system_failure("Failed to open telemetry log");
        return false;
    }
    if (fputs(data, fp) == EOF) {
        fclose(fp);
        return false;
    }
    fclose(fp);
    return true;
}
```

## 4. Key Verification Checklist
- Check all return values from standard I/O, memory allocations, and socket routines.
- In modern C++, utilize `[[nodiscard]]` on crucial functions.
- Ensure that failed operations release all acquired resources before returning error status.
