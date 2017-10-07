#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <iostream>
#include <string>

#include "main/config.h"
#include "main/main.h"

int main() {
	srand(clock()*(time(NULL)%1000));
	// Get username and password. For some reason the returned char array seems to be dereferenced.
	char* userRaw = getpass("Username: "); size_t user_len = strlen(userRaw);
	char* user = (char*)malloc(user_len); strcpy(user, userRaw); wipeNoFree((byte*)userRaw, user_len);
	char* passRaw = getpass("Password: "); size_t pass_len = strlen(passRaw);
	char* pass = (char*)malloc(pass_len); strcpy(pass, passRaw); wipeNoFree((byte*)passRaw, pass_len);
	// Get user hash and wipe user
	std::string userhash = md5hex(user, user_len);
	wipe((byte*)user, user_len); user = NULL;
	// Run Main Loop
	std::string resultString;
	while (resultString != "\n") {
		std::cout << shellString;
		std::cout << (resultString = mainLoop(userhash.c_str(), (const char*)pass));
	}
	// Cleanup
	wipe((byte*)pass, pass_len);
}