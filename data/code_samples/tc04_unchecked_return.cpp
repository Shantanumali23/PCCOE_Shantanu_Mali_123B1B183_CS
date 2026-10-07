// TC04: Unchecked Return Value of System Routine
#include <cstdio>

void recordLogEntry(const char* message) {
    FILE* log_fp = fopen("/tmp/app.log", "a");
    // Defect: log_fp return value is not verified before calling fputs
    fputs(message, log_fp);
    fclose(log_fp);
}

int main() {
    recordLogEntry("System startup initiated");
    return 0;
}
