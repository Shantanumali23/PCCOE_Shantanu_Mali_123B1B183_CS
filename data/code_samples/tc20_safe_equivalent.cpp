// TC20: Safe Defensive Equivalent (No Defects)
#include <iostream>
#include <vector>
#include <memory>
#include <string>

bool processSensorSafely(const std::vector<int>& sensor_data, int index, int& out_value) {
    // Compliant: Validates index against container boundaries
    if (index < 0 || static_cast<size_t>(index) >= sensor_data.size()) {
        std::cerr << "Defensive check: index out of bounds" << std::endl;
        return false;
    }
    out_value = sensor_data[index];
    return true;
}

int main() {
    std::vector<int> sensors = {10, 20, 30};
    int val = 0;
    if (processSensorSafely(sensors, 1, val)) {
        std::cout << "Safe sensor value: " << val << std::endl;
    }
    return 0;
}
