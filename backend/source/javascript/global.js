var urllocation = ""; // Empty string means in the current directory.
// Encryption/Decryption procedures
var hex = sjcl.codec.hex;
var b64 = sjcl.codec.base64;
var str = sjcl.codec.utf8String;
// Function to derive keys using sjcl
function sjclkeydev(key, salt) {
	var saltBits = hex.toBits(hex.fromBits(salt));
	return sjcl.misc.scrypt(key, saltBits, 16384, 8, 1, 512);
}
// Function to encrypt using sjcl
function sjclencrypt(plaintext, key) {
	// Create Values
	var salt = new Uint32Array(4); window.crypto.getRandomValues(salt);
	var iv = new Uint32Array(4); window.crypto.getRandomValues(iv);
	var derived_key = sjclkeydev(key, salt);
	// AES Encryption
	var prp = new sjcl.cipher.aes(sjcl.hash.sha256.hash(derived_key.concat(0)));
	var ciphertextaes = sjcl.mode.gcm.encrypt(prp, plaintext, iv);
	// Salsa20 Encryption
	var salsa = new sjcl.cipher.salsa20(sjcl.hash.sha256.hash(derived_key.concat(~0)), iv.slice(1, 3));
	var ciphertext = salsa.encrypt(ciphertextaes);
	// Concatenate all
	var ciphertextall = hex.fromBits(salt)+hex.fromBits(iv)+hex.fromBits(ciphertext);
	return hex.toBits(ciphertextall);
}
// Function to decrypt using sjcl
function sjcldecrypt(ciphertextall, key) {
	// Import values
	var salt = ciphertextall.slice(0, 4);
	var iv = ciphertextall.slice(4, 8);
	var ciphertext = ciphertextall.slice(8);
	var derived_key = sjclkeydev(key, salt);
	// Salsa20 Decryption
	var salsa = new sjcl.cipher.salsa20(sjcl.hash.sha256.hash(derived_key.concat(~0)), iv.slice(1, 3));
	var ciphertextaes = salsa.decrypt(ciphertext);
	// AES Decryption
	var prp = new sjcl.cipher.aes(sjcl.hash.sha256.hash(derived_key.concat(0)));
	var plaintext = sjcl.mode.gcm.decrypt(prp, ciphertextaes, iv);
	return plaintext;
}
// Function to hash username and account because why not?
function simplehashuser(user) {
	return hex.fromBits(sjcl.misc.scrypt(user, '', 256, 4, 1, 64)); // Parameters chosen for speed - username should be public
}
function simplehashaccount(account, userhash) {
	return hex.fromBits(sjcl.misc.scrypt(account, userhash, 4096, 8, 1, 32)); // Not intended to be very secure
}

// Copies the decrypted password.
function copyAction() {
        var decrypted = document.getElementById("decrypted");
        decrypted.disabled = "";
	decrypted.type = "text";
        decrypted.select();
        document.execCommand("copy");
	decrypted.type = "password";
        decrypted.disabled = "true";
	document.getElementById('notification').className = "notification_success";
	document.getElementById('notification').innerHTML = "Password copied to clipboard.";
}