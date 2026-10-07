// TC08: Integer Overflow in Allocation Sizing
#include <cstdlib>
#include <cstdint>

void* allocateBuffer(uint32_t count, uint32_t item_size) {
    // Defect: Multiplication can overflow 32-bit integer, resulting in a small allocation
    uint32_t total = count * item_size;
    return malloc(total);
}

int main() {
    allocateBuffer(0x80000000, 4);
    return 0;
}
