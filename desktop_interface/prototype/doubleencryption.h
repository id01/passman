#ifndef _UTIL_H
#include "util.h"
#endif

// Derives two keys from one allkeyconst. Allkey should be a 64 byte buffer, and ciphertext should be of size pplaintext_len+32.
// Salt should be of length 16. Returns 1 on success and 0 on failure
int doubleencrypt_backend(const byte* allkeyconst, const byte* plaintext, const size_t plaintext_len, byte* ciphertext) {
	// Declare variables
	byte* allkey = (byte*)malloc(68), *aeskey = (byte*)malloc(32), *salsakey = (byte*)malloc(32);
	// Import key, derive hashes for aes and salsa
	for (int i=0; i<64; i++) { allkey[i] = allkeyconst[i]; }
	allkey[64] = allkey[65] = allkey[66] = allkey[67] = 0;
	CryptoPP::SHA256().CalculateDigest(aeskey, allkey, 68);
	allkey[64] = allkey[65] = allkey[66] = allkey[67] = 0xff;
	CryptoPP::SHA256().CalculateDigest(salsakey, allkey, 68);
	// Allocate ciphertexts and generate IV
	byte* aesCiphertext = (byte*)malloc(plaintext_len+16);
	urandom(ciphertext, 16);
	// Encrypt AES-GCM
	CryptoPP::GCM<CryptoPP::AES>::Encryption aes;
	aes.SetKeyWithIV(aeskey, 32, ciphertext, 16);
	CryptoPP::ArraySource(plaintext, plaintext_len, true,
		new CryptoPP::AuthenticatedEncryptionFilter(
			aes,
			new CryptoPP::ArraySink(aesCiphertext, plaintext_len+16)
		)
	);
	// Encrypt Salsa20
	CryptoPP::Salsa20::Encryption salsa;
	salsa.SetKeyWithIV(salsakey, 32, ciphertext+4, 8);
	salsa.ProcessData(ciphertext+16, aesCiphertext, plaintext_len+16);
	// Cleanup
	wipe(allkey, 68); wipe(aeskey, 32); wipe(salsakey, 32); wipe(aesCiphertext, plaintext_len+16);
	return 1;
}

// Wrapper around doubledecrypt_backend. Ciphertext should have a length of plaintext_len+48. Returns 1 on success and 0 on failure.
int doubleencrypt(const byte* plaintext, const size_t plaintext_len, const byte* password, const size_t password_len, byte* ciphertext) {
	// Generate salt, derive keys, and encrypt
	byte* allkey = (byte*)malloc(64);
	urandom(ciphertext, 16);
	keydev(password, password_len, (const byte*)ciphertext, allkey);
	int result = doubleencrypt_backend(allkey, plaintext, plaintext_len, ciphertext+16);
	// Cleanup and return
	wipe(allkey, 64);
	return result;
}