// TC09: Signed / Unsigned Comparison Mismatch
#include <iostream>
#include <cstddef>

bool isLengthValid(int user_len, size_t max_capacity) {
    // Defect: Negative user_len promotes to large unsigned size_t, bypassing check
    if (user_len > max_capacity) {
        return false;
    }
    return true;
}

int main() {
    bool valid = isLengthValid(-1, 100);
    std::cout << "Is valid: " << valid << std::endl;
    return 0;
}
