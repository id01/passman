function submitAction(event) {
	event.preventDefault();
	var notification = document.getElementById("notification");
	notification.style.color = "";
	notification.innerHTML = "Please wait...";
	var getForm = document.getElementById("getform");
	jQuery.post("getpass.php", "userin=" + getForm.querySelector("[name=userin]").value + "&account=" + getForm.querySelector("[name=account]").value, updateEncrypted, "text");
}
function simpleAESDecrypt(rawciphertext, key) {
	// This is unconventional... Codec aliases
	var cb64 = sjcl.codec.base64;
	var chex = sjcl.codec.hex;
	var cstr = sjcl.codec.utf8String;
	// Decode base64 to hex
	var ciphertext2 = chex.fromBits(cb64.toBits(rawciphertext));
	// Generate keys, get salt
	var salt = ciphertext2.substring(ciphertext2.length-16);
	ciphertext2 = ciphertext2.substring(0, ciphertext2.length-16);
	var shakey1hex = chex.fromBits(sjcl.hash.sha256.hash(cstr.toBits(key)));
	var shakey2 = sjcl.hash.sha256.hash(chex.toBits(shakey1hex+salt));
	var shakey1 = chex.toBits(shakey1hex);
	// First decryption (AES-256-CBC)
	var iv = ciphertext2.substring(0, 32);
	ciphertext2 = ciphertext2.substring(32);
	var ciphertext1 = chex.fromBits(sjcl.mode.cbc.decrypt(new sjcl.cipher.aes(shakey2), chex.toBits(ciphertext2), chex.toBits(iv)));
	// Second decryption (AES-256-GCM)
	iv = ciphertext1.substring(0, 32);
	ciphertext1 = ciphertext1.substring(32);
	var plaintextpad = cstr.fromBits(sjcl.mode.gcm.decrypt(new sjcl.cipher.aes(shakey1), chex.toBits(ciphertext1), chex.toBits(iv)));
	// Unpad plaintext and return
	return plaintextpad.substring(0, plaintextpad.length-plaintextpad.charCodeAt(plaintextpad.length-1));
}
function updateEncrypted(data) {
	// Get data for vars and activate CBC
	var pass = document.getElementById("password_input").value;
	var notification = document.getElementById("notification");
	var encdata = data.split('\n')[0];
	sjcl.beware["CBC mode is dangerous because it doesn't protect message integrity."]();
	// Check output
	if (encdata.substring(0, 6) == "VALID ")
	{
		// Try decryption. If it fails, there is an incorrect password.
		var encPassword = encdata.substring(6);
		var decPassword;
		try {
			decPassword = simpleAESDecrypt(encPassword, pass);
			notification.style.color = "green";
			notification.innerHTML = "Done.";
			document.getElementById("decrypted").value = decPassword;
		}
		catch (err) {
			notification.style.color = "red";
			notification.innerHTML = "Incorrect password.";
		}
	}
	else
	{
		notification.style.color = "red";
		notification.innerHTML = "Error getting entry: "+encdata;
	}
}
function copyAction() {
        var decrypted = document.getElementById("decrypted");
        decrypted.disabled = "";
	decrypted.type = "text";
        decrypted.select();
        document.execCommand("copy");
	decrypted.type = "password";
        decrypted.disabled = "true";
}
