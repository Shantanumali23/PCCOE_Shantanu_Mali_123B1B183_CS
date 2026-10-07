// TC03: Out-of-bounds array access (Off-by-one)
#include <iostream>

void readDiagnostics(int index) {
    int diagnostic_table[5] = {10, 20, 30, 40, 50};
    // Defect: Allowing index <= 5 causes an out-of-bounds read at index == 5
    if (index <= 5) {
        int val = diagnostic_table[index];
        std::cout << "Value: " << val << std::endl;
    }
}

int main() {
    readDiagnostics(5);
    return 0;
}
