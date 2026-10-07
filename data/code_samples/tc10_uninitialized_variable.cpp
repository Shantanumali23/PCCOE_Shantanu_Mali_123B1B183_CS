// TC10: Uninitialized Local Variable
#include <iostream>

bool checkSafetyInterlock(bool sensor_triggered) {
    bool is_safe; // Defect: uninitialized variable
    if (sensor_triggered) {
        is_safe = false;
    }
    // If sensor_triggered is false, is_safe contains garbage stack memory
    return is_safe;
}

int main() {
    std::cout << "Interlock: " << checkSafetyInterlock(false) << std::endl;
    return 0;
}
