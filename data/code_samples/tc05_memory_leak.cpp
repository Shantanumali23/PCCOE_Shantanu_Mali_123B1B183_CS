// TC05: Memory Leak in Premature Return Path
#include <cstdlib>

int processPayload(int error_code) {
    char* buffer = (char*)malloc(1024);
    if (error_code != 0) {
        // Defect: returns early without releasing allocated buffer
        return -1; 
    }
    // Normal processing
    free(buffer);
    return 0;
}

int main() {
    processPayload(1);
    return 0;
}
