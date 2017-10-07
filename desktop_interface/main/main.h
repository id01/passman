#include <string>

typedef unsigned char byte;

void wipeNoFree(byte* buf, size_t buflen);
void wipe(byte* buf, size_t buflen);
std::string md5hex(const char* plaintext, size_t plaintext_len);
std::string mainLoop(const char* userhash, const char* pass);