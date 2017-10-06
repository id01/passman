#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <time.h>

#include <iostream>
#include <string>
#include <sstream>
#include <algorithm>

#define CRYPTOPP_ENABLE_NAMESPACE_WEAK 1
#include <cryptopp/md5.h>
#include <cryptopp/hex.h>
#include <cryptopp/base64.h>
#include <cryptopp/filters.h>

#include "requester.h"
#include "doubledecryption.h"

typedef unsigned char byte;
const char serverURL[] = "http://localhost/passmantest/"; // Must end with slash
const char shellString[] = "passman > "; // Shell string

// Gets an MD5 hash in std::string hex format
std::string md5hex(const char* plaintext, size_t plaintext_len) {
	// Get hash
	byte digest[ CryptoPP::Weak::MD5::DIGESTSIZE ];
	CryptoPP::Weak::MD5 hasher;
	hasher.CalculateDigest( digest, (const byte*)plaintext, plaintext_len );
	// Encode it in hex
	CryptoPP::HexEncoder encoder;
	std::string hash;
	encoder.Attach( new CryptoPP::StringSink( hash ) );
	encoder.Put( digest, sizeof(digest) );
	encoder.MessageEnd();
	// Return
	return hash;
}

// Returns 1 upon exit, 0 otherwise.
int mainLoop(const char* userhash, const char* pass) {
	// Get password length
	size_t pass_len = strlen(pass);
	// Get command from user
	std::string commandRaw;
	std::getline(std::cin, commandRaw);
	std::istringstream commandStream(commandRaw);
	// Parse command
	std::string command;
	commandStream >> command;
	if (command == "GET" || command == "get") { // If command is get
		// Get accountName
		std::string accountName;
		commandStream >> accountName;
		// Get URI of getpass.php
		std::string postURI = serverURL;
		postURI += "getpass.php";
		// Hash account
		std::string accountHash = md5hex(accountName.c_str(), accountName.size());
		// Get POST params
		std::string toPost = "userhash=";
		toPost += userhash;
		toPost += "&account=";
		toPost += accountHash;
		// Change them to lower case
		std::transform(toPost.begin(), toPost.end(), toPost.begin(), ::tolower);
		// Send HTTP request and get Base64 if valid. Cout if not.
		std::string httpresult = httpRequest(postURI, toPost);
		if (httpresult.substr(0, 6) == "VALID ") {
			// Parse base64 string and decode
			std::string passwordRawB64 = httpresult.substr(6);
			CryptoPP::Base64Decoder decoder;
			decoder.Put( (byte*)passwordRawB64.data(), passwordRawB64.size() );
			decoder.MessageEnd();
			size_t ciphertext_len = decoder.MaxRetrievable();
			if (ciphertext_len && ciphertext_len <= SIZE_MAX) {
				byte* ciphertext = (byte*)malloc(ciphertext_len);
				decoder.Get(ciphertext, ciphertext_len);
				// Decrypt!
				size_t plaintext_len = ciphertext_len-48;
				byte* plaintext = (byte*)malloc(plaintext_len+1);
				if (doubledecrypt(ciphertext, ciphertext_len, (const byte*)pass, pass_len, plaintext)) {
					plaintext[plaintext_len] = 0; // Null terminate
					std::cout << "Password: " << plaintext << '\n';
				} else {
					std::cout << "Decryption error.\n";
				}
				// Wipe plaintext
				wipe(plaintext, plaintext_len);
			} else {
				std::cout << "Encoding error.\n";
			}
		} else {
			std::cout << httpresult << '\n'; // There is an error
		}
	} else if (command == "QUIT" || command == "quit" || command == "EXIT" || command == "exit") {
		return 1; // Exit
	} else {
		std::cout << "Command not found.\n";
	}
	return 0;
}

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
	std::cout << shellString;
	while (mainLoop(userhash.c_str(), (const char*)pass) != 1) {
		std::cout << shellString;
	}
	// Cleanup
	wipe((byte*)pass, pass_len);
}