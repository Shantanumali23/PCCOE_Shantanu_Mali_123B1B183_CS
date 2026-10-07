// TC18: Hardcoded Static Credential (Fictional academic demonstration token)
#include <cstring>
#include <iostream>

bool verifyAdminAccess(const char* user_input_token) {
    // Defect: Fictional hardcoded secret token embedded directly in source binary
    const char* MASTER_KEY = "ACADEMIC_TEST_SECRET_KEY_99881";
    if (!user_input_token) return false;
    return strcmp(user_input_token, MASTER_KEY) == 0;
}

int main() {
    bool access = verifyAdminAccess("TEST");
    std::cout << "Access: " << access << std::endl;
    return 0;
}
