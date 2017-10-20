#include <string>

#include <python2.7/Python.h>

#include <cryptopp/eccrypto.h>
#include <cryptopp/asn.h>
#include <cryptopp/oids.h>
#include <cryptopp/osrng.h>
#include <cryptopp/ecp.h>
#include <cryptopp/filters.h>
#include <cryptopp/sha.h>

// Default Error String
const char defaultErrorString[] = "You should never get this error, but if you do, it is certain that something very bad happened. I have no idea what it is.";

// Exceptions
static PyObject *EncodingError, *ExecutionalError, *ExceptionalException;

// Usage: signECDSA(plaintext, privateKeyDer)
PyObject* ecdsalib_signECDSA(PyObject* self, PyObject* args) {
	// Get Python Arguments
	byte *plaintextraw, *privkeyder;
	int plaintextraw_len, privkeyder_len;
	if (!PyArg_ParseTuple(args, "s#s#", &plaintextraw, &plaintextraw_len, &privkeyder, &privkeyder_len)) return NULL;
	try {
		// Load Private Key to object from array
		CryptoPP::ECDSA<CryptoPP::ECP, CryptoPP::SHA256>::PrivateKey privkeyobj;
		CryptoPP::ArraySource arrs(privkeyder, privkeyder_len, true);
		try {
			privkeyobj.Load(arrs);
		} catch (const CryptoPP::Exception& ex) {
			PyErr_SetString(EncodingError, ex.what()); return NULL;
		}
		// Sign
		std::string signature;
		CryptoPP::AutoSeededRandomPool prng;
		CryptoPP::ECDSA<CryptoPP::ECP, CryptoPP::SHA256>::Signer signer(privkeyobj);
		CryptoPP::ArraySource(plaintextraw, plaintextraw_len, true,
			new CryptoPP::SignerFilter(prng,
				signer,
				new CryptoPP::StringSink(signature)
			)
		);
		// Return
		std::string sig(signature);
		return Py_BuildValue("s#", signature.c_str(), signature.size());
	} catch (const std::exception& ex) {
		PyErr_SetString(ExecutionalError, ex.what());
	} catch (const std::string& ex) {
		PyErr_SetString(ExecutionalError, ex.c_str());
	} catch (...) {
		PyErr_SetString(ExceptionalException, defaultErrorString);
	}
	return NULL;
}

// Usage: signECDSA(plaintext, signature, publicKeyDer)
PyObject* ecdsalib_verifyECDSA(PyObject* self, PyObject* args) {
	// Get Python Arguments
	byte *plaintextraw, *signature, *pubkeyder;
	int plaintextraw_len, signature_len, pubkeyder_len;
	if (!PyArg_ParseTuple(args, "s#s#s#", &plaintextraw, &plaintextraw_len, &signature, &signature_len, &pubkeyder, &pubkeyder_len)) return NULL;
	// Load Private Key to object from array
	try {
		CryptoPP::ECDSA<CryptoPP::ECP, CryptoPP::SHA256>::PublicKey pubkeyobj;
		CryptoPP::ArraySource arrs(pubkeyder, pubkeyder_len, true);
		try {
			pubkeyobj.Load(arrs);
		} catch (const CryptoPP::Exception& ex) {
			PyErr_SetString(EncodingError, ex.what()); return NULL;
		}
		// Sign
		bool result = false;
		byte* toVerify = (byte*)malloc(signature_len + plaintextraw_len);
		for (int i=0; i<signature_len; i++) { toVerify[i] = signature[i]; }
		for (int i=0; i<plaintextraw_len; i++) { toVerify[i+signature_len] = plaintextraw[i]; }
		CryptoPP::ECDSA<CryptoPP::ECP, CryptoPP::SHA256>::Verifier verifier(pubkeyobj);
		CryptoPP::ArraySource(toVerify, signature_len+plaintextraw_len, true,
			new CryptoPP::SignatureVerificationFilter(
				verifier,
				new CryptoPP::ArraySink((byte*)&result, 1)
			)
		);
		// Return
		return Py_BuildValue("i", result);
	} catch (const std::exception& ex) {
		PyErr_SetString(ExecutionalError, ex.what());
	} catch (const std::string& ex) {
		PyErr_SetString(ExecutionalError, ex.c_str());
	} catch (...) {
		PyErr_SetString(ExceptionalException, defaultErrorString);
	}
	return NULL;
}

static PyMethodDef MethodList[] = {
	{"signECDSA", ecdsalib_signECDSA, METH_VARARGS, "Signs a string with ECDSA"},
	{"verifyECDSA", ecdsalib_verifyECDSA, METH_VARARGS, "Verifies an ECDSA signature"},
	{NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initecdsalib(void) {
	PyObject *m;
	m = Py_InitModule("ecdsalib", MethodList);
	if (m == NULL) return;
	EncodingError = PyErr_NewException((char*)"ecdsalib.EncodingError", NULL, NULL);
	Py_INCREF(EncodingError);
	PyModule_AddObject(m, "error", EncodingError);
	ExecutionalError = PyErr_NewException((char*)"ecdsalib.ExecutionalError", NULL, NULL);
	Py_INCREF(ExecutionalError);
	PyModule_AddObject(m, "error", ExecutionalError);
	ExceptionalException = PyErr_NewException((char*)"ecdsalib.ExceptionalException", NULL, NULL);
	Py_INCREF(ExceptionalException);
	PyModule_AddObject(m, "error", ExceptionalException);
}

int main(int argc, char* argv[]) {
	Py_SetProgramName(argv[0]);
	Py_Initialize();
	initecdsalib();
}