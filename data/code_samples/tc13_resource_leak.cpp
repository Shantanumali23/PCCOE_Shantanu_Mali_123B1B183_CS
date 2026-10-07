// TC13: Resource Leak (Unclosed File Descriptor)
#include <cstdio>

int dumpTelemetryData(const char* filepath, const char* content) {
    FILE* fp = fopen(filepath, "w");
    if (!fp) return -1;

    if (!content) {
        // Defect: Early return without closing file descriptor fp
        return -2;
    }

    fputs(content, fp);
    fclose(fp);
    return 0;
}

int main() {
    dumpTelemetryData("/tmp/telemetry.txt", nullptr);
    return 0;
}
