# Synthetic educational knowledge base created for academic demonstration.

# Guideline: KB-HIST-002 — Historical Defect: Network Packet Underflow in Frame Unpacking
**Category**: Historical Findings  
**Topic**: CAN/Ethernet Frame Parsing  
**Citation Code**: KB-HIST-002  
**Severity Default**: High  

## 1. Case History
A historical telematics gateway driver unpacked payload lengths by subtracting header offsets without first verifying that the packet length was greater than or equal to the minimum header size. Small malformed packets caused an arithmetic underflow, producing an enormous `size_t` value that caused downstream buffer over-reads.

## 2. Root Cause Identified
Implicit underflow:
```cpp
size_t payload_len = total_received - HEADER_SIZE; // Underflows if total_received < HEADER_SIZE
```

## 3. Preventive Rule
Always verify that total length exceeds the fixed header length before subtraction:
```cpp
if (total_received < HEADER_SIZE) {
    drop_malformed_packet();
    return;
}
size_t payload_len = total_received - HEADER_SIZE;
```
Related Guidelines: KB-SEC-002, KB-INPUT-002.
