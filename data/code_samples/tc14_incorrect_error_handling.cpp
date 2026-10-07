// TC14: Incorrect Error Handling (Suppressed Failure Status)
#include <iostream>

bool performCalibration(int sensor_id) {
    if (sensor_id < 0) {
        // Defect: Logs warning but returns true, propagating invalid state downstream
        std::cerr << "Warning: sensor_id is negative" << std::endl;
        return true; 
    }
    return true;
}

int main() {
    bool ok = performCalibration(-10);
    std::cout << "Calibration status: " << ok << std::endl;
    return 0;
}
