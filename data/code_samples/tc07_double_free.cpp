// TC07: Double Free Flaw
#include <cstdlib>

void deallocateMemory(char* buffer) {
    free(buffer);
    // Defect: Re-freeing the same pointer without setting it to nullptr
    free(buffer);
}

int main() {
    char* data = (char*)malloc(64);
    deallocateMemory(data);
    return 0;
}
