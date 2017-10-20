function generateSubmitForm() {
	// Get user input
	var username = document.getElementById('username_input').value;
	var password = document.getElementById('password_input').value;
	var notification = document.getElementById("notification");
	if (password != document.getElementById('password2').value) {
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
		document.getElementById('userhash').value = simplehashuser(username.toLowerCase());
		document.getElementById('public').value = b64.fromBits(hex.toBits(new KJUR.asn1.x509.SubjectPublicKeyInfo(ec).getEncodedHex()));
		// Encrypt private key
		var prvKeyB64 = KEYUTIL.getPEM(ec, "PKCS8PRV").replace('-----BEGIN PRIVATE KEY-----', '').replace('-----END PRIVATE KEY-----', '').replace(/\n/g, '').trim();
		document.getElementById('encryptedprivate').value = b64.fromBits(sjclencrypt(b64.toBits(prvKeyB64), password));
		document.getElementById('serverauth').value = document.getElementById('auth').value;
		document.getElementById('submitform').submit();
	}, 20);
}
