// TC15: Infinite Loop Condition in Unsigned Countdown
#include <iostream>

void countdownTimer(unsigned int seconds) {
    // Defect: seconds is unsigned; when it reaches 0, seconds-- wraps to UINT_MAX, causing an infinite loop
    for (; seconds >= 0; seconds--) {
        std::cout << "Tick: " << seconds << std::endl;
        if (seconds == 0) break; // Defensive guard omitted in defect
    }
}

int main() {
    countdownTimer(3);
    return 0;
}
