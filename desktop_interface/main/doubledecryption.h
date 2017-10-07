#ifndef _UTIL_H
#include "util.h"
#endif

// Derives two keys from one allkeyconst. Allkey should be a 64 byte buffer, and plaintext should be of size ciphertext_len-32.
// Salt should be of length 16. Returns 1 on success and 0 on failure
int doubledecrypt_backend(const byte* allkeyconst, const byte* ciphertext, const size_t ciphertext_len, byte* plaintext) {
	// Declare variables
	byte* allkey = (byte*)malloc(68), *aeskey = (byte*)malloc(32), *salsakey = (byte*)malloc(32);
	// Import key, derive hashes for aes and salsa
	for (int i=0; i<64; i++) { allkey[i] = allkeyconst[i]; }
	allkey[64] = allkey[65] = allkey[66] = allkey[67] = 0;
	CryptoPP::SHA256().CalculateDigest(aeskey, allkey, 68);
	allkey[64] = allkey[65] = allkey[66] = allkey[67] = 0xff;
	CryptoPP::SHA256().CalculateDigest(salsakey, allkey, 68);
	// Decrypt Salsa20
	byte* aesCiphertext = (byte*)malloc(ciphertext_len-16);
	CryptoPP::Salsa20::Decryption salsa;
	salsa.SetKeyWithIV(salsakey, 32, ciphertext+4, 8);
	salsa.ProcessData(aesCiphertext, ciphertext+16, ciphertext_len-16);
	// Decrypt AES-GCM
	CryptoPP::GCM<CryptoPP::AES>::Decryption aes;
	aes.SetKeyWithIV(aeskey, 32, ciphertext, 16);
	try {
		CryptoPP::ArraySource(aesCiphertext, ciphertext_len-16, true,
			new CryptoPP::AuthenticatedDecryptionFilter(
				aes,
				new CryptoPP::ArraySink(plaintext, ciphertext_len-32)
			)
		);
	} catch (CryptoPP::HashVerificationFilter::HashVerificationFailed e) {
		return 0;
	}
	// Cleanup
	wipe(allkey, 68); wipe(aeskey, 32); wipe(salsakey, 32); wipe(aesCiphertext, ciphertext_len-16);
	return 1;
}

// Wrapper around doubledecrypt_backend. Plaintext should have a length of ciphertext_len-48. Returns 1 on success and 0 on failure.
int doubledecrypt(const byte* ciphertext, const size_t ciphertext_len, const byte* password, const size_t password_len, byte* plaintext) {
	// Derive keys and encrypt
	byte* allkey = (byte*)malloc(64);
	keydev(password, password_len, (const byte*)ciphertext, allkey);
	int result = doubledecrypt_backend(allkey, ciphertext+16, ciphertext_len-16, plaintext);
	// Cleanup and return
	wipe(allkey, 64);
	return result;
}