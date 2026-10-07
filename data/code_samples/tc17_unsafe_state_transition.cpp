// TC17: Unsafe State Machine Transition
#include <iostream>

enum SystemState { INIT = 0, READY = 1, ARMED = 2, FIRED = 3 };

static SystemState g_state = INIT;

void fireActuator() {
    // Defect: Directly transitions to FIRED without verifying precondition (ARMED)
    g_state = FIRED;
    std::cout << "Actuator triggered!" << std::endl;
}

int main() {
    fireActuator();
    return 0;
}
