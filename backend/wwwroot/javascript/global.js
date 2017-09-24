var urllocation = ""; // Empty string means in the current directory.
// Encryption/Decryption procedures
var hex = sjcl.codec.hex;
var b64 = sjcl.codec.base64;
var str = sjcl.codec.utf8String;
/*function sjclencryptaes(plaintext, key) {
	var salt = new Uint32Array(4); window.crypto.getRandomValues(salt);
	var iv = new Uint32Array(4); window.crypto.getRandomValues(iv);
	var prp = new sjcl.cipher.aes(sjcl.misc.pbkdf2(key, hex.toBits(hex.fromBits(salt)), 8192, 256));
	var ciphertext = sjcl.mode.gcm.encrypt(prp, plaintext, iv);
	var ciphertextall = hex.fromBits(salt)+hex.fromBits(iv)+hex.fromBits(ciphertext);
	return hex.toBits(ciphertextall);
}
function sjcldecryptaes(ciphertextall, key) {
	var salt = ciphertextall.slice(0, 4);
	var iv = ciphertextall.slice(4, 8);
	var ciphertext = ciphertextall.slice(8);
	var prp = new sjcl.cipher.aes(sjcl.misc.pbkdf2(key, hex.toBits(hex.fromBits(salt)), 8192, 256));
	var plaintext = sjcl.mode.gcm.decrypt(prp, ciphertext, iv);
	return plaintext;
}*/
function sjclkeydev(key, salt) {
	var saltBits = hex.toBits(hex.fromBits(salt));
	var pbkdf2key = sjcl.misc.pbkdf2(key, saltBits, 8192, 256);
	var scryptkey = sjcl.misc.scrypt(key, saltBits, 8192, 8, 1, 256);
	return sjcl.hash.sha256.hash(pbkdf2key.concat(scryptkey));
}
function sjclencrypt(plaintext, key) {
	// Create Values
	var salt = new Uint32Array(4); window.crypto.getRandomValues(salt);
	var iv = new Uint32Array(4); window.crypto.getRandomValues(iv);
	var derived_key = sjclkeydev(key, salt);
	// AES Encryption
	var prp = new sjcl.cipher.aes(sjcl.hash.sha256.hash(derived_key.concat(new Uint32Array([0]))));
	var ciphertextaes = sjcl.mode.gcm.encrypt(prp, plaintext, iv);
	// Salsa20 Encryption
	var salsa = new sjcl.cipher.salsa20(sjcl.hash.sha256.hash(derived_key.concat(new Uint32Array([~0]))), iv.slice(1, 3));
	var ciphertext = salsa.encrypt(ciphertextaes);
	// Concatenate all
	var ciphertextall = hex.fromBits(salt)+hex.fromBits(iv)+hex.fromBits(ciphertext);
	return hex.toBits(ciphertextall);
}
function sjcldecrypt(ciphertextall, key) {
	// Import values
	var salt = ciphertextall.slice(0, 4);
	var iv = ciphertextall.slice(4, 8);
	var ciphertext = ciphertextall.slice(8);
	var derived_key = sjclkeydev(key, salt);
	// Salsa20 Decryption
	var salsa = new sjcl.cipher.salsa20(sjcl.hash.sha256.hash(derived_key.concat(new Uint32Array([~0]))), iv.slice(1, 3));
	var ciphertextaes = salsa.decrypt(ciphertext);
	// AES Decryption
	var prp = new sjcl.cipher.aes(sjcl.hash.sha256.hash(derived_key.concat(new Uint32Array([0]))));
	var plaintext = sjcl.mode.gcm.decrypt(prp, ciphertextaes, iv);
	return plaintext;
}