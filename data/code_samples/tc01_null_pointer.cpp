// TC01: Null Pointer Dereference in Sensor Ingestion
#include <iostream>

void processSensor(int* sensor) {
    // Defect: sensor pointer is dereferenced directly without checking for nullptr
    int value = sensor[0];
    std::cout << "Sensor value: " << value << std::endl;
}

int main() {
    int* bad_sensor = nullptr;
    processSensor(bad_sensor);
    return 0;
}
