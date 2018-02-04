// Optimize getElementById calls
function getElementById(name) {
	return document.getElementById(name);
}

// Generates the form to submit and submits it.
function generateSubmitForm() {
	// Get user input
	var username = getElementById('username_input').value;
	var password = getElementById('password_input').value;
	var notification = getElementById("notification");
	if (password != getElementById('password2').value) {
		notification.value = "Passwords don't match.";
		notification.className = "notification_failure";
		return;
	}
	// Generate key pair
	notification.innerHTML = "Generating secrets...";
	var ec = new KJUR.crypto.ECDSA({"curve": "secp256k1"});
	ec.generateKeyPairHex();
	// Encrypt secrets
	notification.innerHTML = "Encrypting secrets...";
	setTimeout(function() {
		// Transfer data to hidden form
		getElementById('userhash').value = simplehashuser(username.toLowerCase());
		getElementById('public').value = b64.fromBits(hex.toBits(new KJUR.asn1.x509.SubjectPublicKeyInfo(ec).getEncodedHex()));
		// Encrypt private key
		var prvKeyB64 = KEYUTIL.getPEM(ec, "PKCS8PRV").replace('-----BEGIN PRIVATE KEY-----', '').replace('-----END PRIVATE KEY-----', '').replace(/\n/g, '').trim();
		getElementById('encryptedprivate').value = b64.fromBits(sjclencrypt(b64.toBits(prvKeyB64), password));
		getElementById('serverauth').value = getElementById('auth').value;
		getElementById('submitform').submit();
	}, 20);
}
