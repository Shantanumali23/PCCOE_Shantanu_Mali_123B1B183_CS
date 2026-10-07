// TC02: Stack Buffer Overflow via Unbounded String Copy
#include <cstring>
#include <iostream>

void copyTelemetryTag(const char* input_tag) {
    char local_buffer[16];
    // Defect: strcpy does not check length of input_tag against buffer capacity
    strcpy(local_buffer, input_tag);
    std::cout << "Tag: " << local_buffer << std::endl;
}

int main() {
    copyTelemetryTag("OVERSIZED_TELEMETRY_PACKET_HEADER_OVERFLOW");
    return 0;
}
