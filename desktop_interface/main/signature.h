#include <stdlib.h>

#include <string>
#include <iostream>

#include <cryptopp/eccrypto.h>
#include <cryptopp/asn.h>
#include <cryptopp/oids.h>
#include <cryptopp/osrng.h>
#include <cryptopp/ecp.h>
#include <cryptopp/filters.h>
#include <cryptopp/sha.h>
#include <cryptopp/hex.h>

std::string create_signature(const std::string plaintext, const byte* privkey, const size_t privkey_len) {
	// Create objects
	std::string signature;
	CryptoPP::AutoSeededRandomPool prng;
	// Load Private key to object from array
	CryptoPP::ECDSA<CryptoPP::ECP, CryptoPP::SHA256>::PrivateKey privkeyobj;
	CryptoPP::ArraySource arrs(privkey, privkey_len, true);
	privkeyobj.Load(arrs);
	// Sign
	CryptoPP::ECDSA<CryptoPP::ECP, CryptoPP::SHA256>::Signer signer(privkeyobj);
	CryptoPP::StringSource s(plaintext, true,
		new CryptoPP::SignerFilter(prng,
			signer,
			new CryptoPP::StringSink(signature)
		)
	);
	// Return
	return signature;
}