// TC12: Unsafe String Formatting Operation
#include <cstdio>

void formatErrorMessage(const char* module_name, const char* detail) {
    char out_buf[32];
    // Defect: sprintf without buffer bounding can easily overrun out_buf
    sprintf(out_buf, "ERROR in %s: %s", module_name, detail);
    printf("%s\n", out_buf);
}

int main() {
    formatErrorMessage("CAN_DRIVER_SUBSYSTEM_EXTENDED", "CRITICAL_TIMING_VIOLATION_ENCOUNTERED");
    return 0;
}
