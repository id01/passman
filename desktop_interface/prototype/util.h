#include <stdlib.h>
#include <stdio.h>

#include <cryptopp/sha.h>
#include <cryptopp/pwdbased.h>
#include <cryptopp/salsa.h>
#include <cryptopp/aes.h>
#include <cryptopp/modes.h>
#include <cryptopp/gcm.h>
#include <cryptopp/filters.h>

#include "libscrypt/libscrypt.h"

#define _UTIL_H

typedef unsigned char byte;

// Wipes a pointer without freeing it
void wipeNoFree(byte* buf, size_t buflen) {
	for (size_t i=0; i<buflen; i++) {
		buf[i] = rand()%256;
	}
}

// Wipes a pointer
void wipe(byte* buf, size_t buflen) {
	wipeNoFree(buf, buflen);
	free(buf);
}

// Gets a SHA256 hash.
void sha256(const byte* buffer, size_t buffer_len, byte* output) {
	CryptoPP::SHA256().CalculateDigest(output, buffer, buffer_len);
}

// Derives a key. Out buffer should be 64 bytes. Salt should be 16 bytes.
void keydev(const byte* password, size_t password_len, const byte* salt, byte* outbuf) {
	CryptoPP::PKCS5_PBKDF2_HMAC<CryptoPP::SHA256> pbkdf2;
	pbkdf2.DeriveKey(outbuf, 32, 0, password, password_len, salt, 16, 8192);
	libscrypt_scrypt(password, password_len, salt, 16, 8192, 8, 1, outbuf+32, 32);
}

// Randomizes byte array
void urandom(byte* buf, size_t buflen) {
	FILE* devurandom = fopen("/dev/urandom", "r");
	for (size_t i=0; i<buflen; i++) {
		buf[i] = fgetc(devurandom);
	}
	fclose(devurandom);
}