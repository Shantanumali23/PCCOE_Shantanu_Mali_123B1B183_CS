// TC19: Unbounded Pointer Arithmetic Beyond Array Boundary
#include <iostream>

void clearArray(int* start_ptr, int length) {
    // Defect: Increments pointer without checking against buffer boundary
    for (int i = 0; i <= length; i++) {
        *start_ptr = 0;
        start_ptr++; // Points out of bounds on the final iteration
    }
}

int main() {
    int arr[4] = {1, 2, 3, 4};
    clearArray(arr, 4);
    return 0;
}
