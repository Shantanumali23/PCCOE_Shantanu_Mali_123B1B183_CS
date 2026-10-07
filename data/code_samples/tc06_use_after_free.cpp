// TC06: Use-After-Free Vulnerability
#include <cstdlib>
#include <iostream>

struct PacketHeader {
    int id;
    int length;
};

void handleHeader() {
    PacketHeader* hdr = (PacketHeader*)malloc(sizeof(PacketHeader));
    hdr->id = 101;
    free(hdr);
    // Defect: Dereferencing pointer after it has been freed
    std::cout << "Freed header ID: " << hdr->id << std::endl;
}

int main() {
    handleHeader();
    return 0;
}
