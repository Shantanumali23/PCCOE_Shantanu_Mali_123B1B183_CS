// TC11: Weak Input Validation on Network Packet Length
#include <cstring>
#include <cstdint>

void parseNetworkFrame(const uint8_t* raw_bytes, uint32_t length) {
    uint8_t internal_buffer[128];
    // Defect: Length is not verified against internal_buffer size (128)
    memcpy(internal_buffer, raw_bytes, length);
}

int main() {
    uint8_t payload[512] = {0};
    parseNetworkFrame(payload, 512);
    return 0;
}
