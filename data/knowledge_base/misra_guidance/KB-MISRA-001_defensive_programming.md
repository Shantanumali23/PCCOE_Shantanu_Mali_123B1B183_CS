# Synthetic educational knowledge base created for academic demonstration.

# Guideline: KB-MISRA-001 — Defensive Programming & Assertion Placement
**Category**: MISRA-Oriented Guidance  
**Topic**: Defensive Programming  
**Citation Code**: KB-MISRA-001  
**Severity Default**: Medium  

## 1. Educational Overview
*Educational summary inspired by automotive/embedded defensive engineering practices. Not an official MISRA standard publication.*

Defensive programming requires that software routines explicitly anticipate unexpected inputs, states, and anomalous external events rather than assuming benign preconditions. Invariants should be checked and default fallback states explicitly provided.

## 2. Guideline Rules
1. Every `switch` statement must feature a terminating `default` clause, even when all enumerated values appear to be covered.
2. In safety loops, ensure loop counters and termination conditions are monotonically bounded to avoid infinite cycling.
3. Preconditions must be verified at public module boundaries.

## 3. Vulnerability Pattern
Missing default clause in critical state evaluation:
```cpp
enum ActuatorState { IDLE, RUNNING, STOPPED };

void transitionState(ActuatorState state) {
    switch(state) {
        case IDLE: stopMotor(); break;
        case RUNNING: startMotor(); break;
        // VIOLATION: missing default clause to handle invalid memory state or corrupted enum
    }
}
```

## 4. Remediation
```cpp
void transitionState(ActuatorState state) {
    switch(state) {
        case IDLE: stopMotor(); break;
        case RUNNING: startMotor(); break;
        case STOPPED: lockBrakes(); break;
        default:
            // Safe fallback state for safety-critical systems
            emergencySafeShutdown();
            break;
    }
}
```
