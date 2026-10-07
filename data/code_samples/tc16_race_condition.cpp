// TC16: Race Condition (Unsynchronized Shared Global State)
#include <iostream>

static int g_shared_counter = 0;

void workerThreadIncrement() {
    // Defect: Shared variable modified concurrently without mutex locking or atomic semantics
    int current = g_shared_counter;
    current = current + 1;
    g_shared_counter = current;
}

int main() {
    workerThreadIncrement();
    std::cout << "Counter: " << g_shared_counter << std::endl;
    return 0;
}
