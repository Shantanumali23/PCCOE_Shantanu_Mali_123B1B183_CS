# Synthetic educational knowledge base created for academic demonstration.

# Guideline: KB-HIST-001 — Historical Defect: Sensor Telemetry Pointer Dereference
**Category**: Historical Findings  
**Topic**: Embedded Sensor Handling  
**Citation Code**: KB-HIST-001  
**Severity Default**: High  

## 1. Case History
In a previous revision of the embedded vehicle telemetry firmware, sensor reading functions assumed that hardware ADC buffers were always initialized. Under rapid ignition power-cycling, the hardware abstraction layer returned `nullptr`, leading to an instant system crash during sensor telemetry ingestion.

## 2. Root Cause Identified
The ingestion function `processSensor(int* sensor)` assumed caller validation and omitted an internal null pointer check.

## 3. Preventive Rule
Functions that accept pointer arguments must assume external components may fail and provide explicit defensive guards.
```cpp
void processSensor(const int* sensor) {
    if (!sensor) {
        log_sensor_fault();
        return;
    }
    int val = sensor[0];
}
```
Related Guidelines: KB-MEM-001, KB-MISRA-001.
