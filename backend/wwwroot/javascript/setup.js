function generateSubmitForm() {
	var username = document.getElementById('username_input').value;
	var password = document.getElementById('password_input').value;
	if (password != document.getElementById('password2').value) {
		document.getElementById('errordiv').style.display = "block";
		document.getElementById('errordiv').value = "Passwords don't match.";
		return;
	}
	// Generate key pair
	document.getElementById("status").innerHTML = "Generating secrets...";
	var ec = new KJUR.crypto.ECDSA({"curve": "secp256k1"});
	var keypair = ec.generateKeyPairHex();
	// Encrypt secrets
	document.getElementById("status").innerHTML = "Encrypting secrets...";
	setTimeout(function() {
		// Transfer data to hidden form
		document.getElementById('userhash').value = md5(username.toLowerCase());
		document.getElementById('public').value = b64.fromBits(hex.toBits(new KJUR.asn1.x509.SubjectPublicKeyInfo(ec).getEncodedHex()));
		// Encrypt private key
		document.getElementById('status').style.display = "block";
		var prvKeyB64 = KEYUTIL.getPEM(ec, "PKCS8PRV").replace('-----BEGIN PRIVATE KEY-----', '').replace('-----END PRIVATE KEY-----', '').replace(/\n/g, '').trim();
		document.getElementById('encryptedprivate').value = b64.fromBits(sjclencrypt(b64.toBits(prvKeyB64), password));
		document.getElementById('serverauth').value = document.getElementById('auth').value;
		document.getElementById('submitform').submit();
	}, 20);
}