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
#include "doubleencryption.h"
#include "signature.h"

typedef unsigned char byte;
const char serverURL[] = "http://localhost/passmantest/"; // Must end with slash
const char shellString[] = "passman > "; // Shell string

byte* eccprivkey = NULL;
size_t eccprivkey_len = 0;

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

// Returns string on exit containg result, empty string otherwise
std::string mainLoop(const char* userhash, const char* pass) {
	// Create stringstream
	std::stringstream resultStream("");
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
					resultStream << "Password: " << plaintext << '\n';
				} else {
					resultStream << "Decryption error.\n";
				}
				// Wipe plaintext
				wipe(plaintext, plaintext_len);
			} else {
				resultStream << "Encoding error.\n";
			}
		} else {
			resultStream << httpresult << '\n'; // There is an error
		}
	} else if (command == "ADD" || command == "add") { // If command is add
		// Get accountName and passLength
		std::string accountName, passLength;
		commandStream >> accountName >> passLength;
		// Get URI of addpass_challenge.php
		std::string postURI = serverURL;
		postURI += "addpass_challenge.php";
		// Hash account
		std::string accountHash = md5hex(accountName.c_str(), accountName.size());
		std::transform(accountHash.begin(), accountHash.end(), accountHash.begin(), ::tolower);
		// Get POST params
		std::string toPost = "userhash=";
		toPost += userhash;
		toPost += "&account=";
		toPost += accountHash;
		// Change them to lower case
		std::transform(toPost.begin(), toPost.end(), toPost.begin(), ::tolower);
		// Send HTTP, while storing cookies
		std::string httpresult = httpRequest(postURI, toPost, 1);
		// Parse output and return on error
		std::string challenge, eccprivkeyraw, status, eccprivkeyb64, eccprivkeyenc;
		if (httpresult.find('\n') != -1) {
			challenge = httpresult.substr(0, httpresult.find('\n'));
			eccprivkeyraw = httpresult.substr(httpresult.find('\n'));
			std::istringstream eccprivkeystream(eccprivkeyraw);
			eccprivkeystream >> status >> eccprivkeyb64;
		} else {
			eccprivkeyraw = httpresult;
			status = "NOPE";
		}
		if (status == "VALID") { // If no error
			if (eccprivkey == NULL || eccprivkey_len == 0) { // Decrypt private key. We haven't done so yet.
				// Decode key
				CryptoPP::StringSource(eccprivkeyb64, true,
					new CryptoPP::Base64Decoder(
						new CryptoPP::StringSink(eccprivkeyenc)
					)
				);
				// Decrypt key
				eccprivkey_len = eccprivkeyenc.size()-48;
				eccprivkey = (byte*)malloc(eccprivkey_len);
				if (!doubledecrypt((const byte*)eccprivkeyenc.c_str(), eccprivkeyenc.size(), (const byte*)pass, pass_len, eccprivkey)) {
					resultStream << "Decryption error.\n";
				}
			}
			// Generate a password of length passLength
			int newPassword_len = atoi(passLength.c_str());
			if (newPassword_len == 0) {
				resultStream << "Password length must be an integer\n";
				return resultStream.str();
			}
			const char* possiblechars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.!";
			byte* newPasswordBytes = (byte*)malloc(newPassword_len);
			char* newPassword = (char*)malloc(newPassword_len);
			for (int i=0; i<newPassword_len; i++) {
				newPassword[i] = possiblechars[newPasswordBytes[i] >> 2];
			}
			// Encrypt newPassword
			byte* encryptedPassword = (byte*)malloc(newPassword_len+48);
			if (doubleencrypt((const byte*)newPassword, newPassword_len, (const byte*)pass, pass_len, encryptedPassword)) { // If encryption succeeded
				// Encode encryptedPassword in base64 and remove newlines
				std::string encryptedPasswordB64;
				CryptoPP::ArraySource(encryptedPassword, newPassword_len+48, true, 
					new CryptoPP::Base64Encoder(
						new CryptoPP::StringSink(encryptedPasswordB64)
					)
				);
				size_t pos = 0;
				while ((pos = encryptedPasswordB64.find('\n', pos)) != std::string::npos) {
					encryptedPasswordB64.replace(pos, 1, "");
				}
				// Sign and encode b64
				std::stringstream toSign("");
				toSign << challenge << '$' << accountHash << '$' << encryptedPasswordB64;
				std::cout << toSign.str() << '\n';
				std::string signature = create_signature(toSign.str(), eccprivkey, eccprivkey_len), signatureB64;
				CryptoPP::StringSource(signature, true,
					new CryptoPP::Base64Encoder(
						new CryptoPP::StringSink(signatureB64)
					)
				);
				// Send HTTP again
				postURI = serverURL;
				postURI += "addpass_verify.php";
				toPost = "userhash=";
				toPost += userhash;
				toPost += "&passwordcrypt=";
				toPost += encryptedPasswordB64;
				toPost += "&signature=";
				toPost += signatureB64;
				// URL encode '+' and remove '\n'
				pos = 0;
				while ((pos = toPost.find('+', pos)) != std::string::npos) {
					toPost.replace(pos, 1, "%2B");
					pos += 3;
				}
				pos = 0;
				while ((pos = toPost.find('\n', pos)) != std::string::npos) {
					toPost.replace(pos, 1, "");
				}
				std::cout << toPost << '\n';
				httpresult = httpRequest(postURI, toPost, 2);
				// Cleanup and Return
				wipe((byte*)newPassword, newPassword_len); wipe(newPasswordBytes, newPassword_len); free(encryptedPassword);
				resultStream << httpresult << '\n';
			} else {
				resultStream << "Encryption error.\n";
			}
		} else {
			resultStream << eccprivkeyraw << '\n';
		}
	} else if (command == "QUIT" || command == "quit" || command == "EXIT" || command == "exit") {
		// Do nothing
	} else {
		resultStream << "Command not found.\n";
	}
	return resultStream.str();
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
	std::string resultString;
	do {
		std::cout << shellString;
		std::cout << (resultString = mainLoop(userhash.c_str(), (const char*)pass));
	} while (resultString != "");
	// Cleanup
	wipe((byte*)pass, pass_len);
}