function updateStatus(statusObject) {
	var statusSpan = document.getElementById("status");
	statusSpan.innerHTML = statusObject.what + ' - ' + (Math.ceil(1000*statusObject.i/statusObject.total)/10) + '...';
}
function generateSubmitForm() {
	var username = document.getElementById('username_input').value;
	var password = document.getElementById('password_input').value;
	if (password != document.getElementById('password2').value) {
		document.getElementById('errordiv').style.display = "block";
		document.getElementById('errordiv').value = "Passwords don't match.";
		return;
	}
	document.getElementById("status").innerHTML = "Generating keys...";
	// Generate key pair
	var ec = new KJUR.crypto.ECDSA({"curve": "secp256k1"});
	var keypair = ec.generateKeyPairHex();
	// Transfer data to hidden form
	document.getElementById('userhash').value = md5(username);
	document.getElementById('public').value = new KJUR.asn1.x509.SubjectPublicKeyInfo(ec).getEncodedHex();
	// Encrypt private key
	document.getElementById('status').style.display = "block";
	triplesec.encrypt({
		data: new triplesec.Buffer(keypair.ecprvhex, 'hex'),
		key: new triplesec.Buffer(password),
		progress_hook: updateStatus
	}, function (err, buf) {
		if (!err) {
			// Submit hidden form
			document.getElementById('encryptedprivate').value = buf.toString('base64');
			document.getElementById('serverauth').value = document.getElementById('auth').value;
			document.getElementById('submitform').submit();
		} else {
			document.getElementById('errordiv').style.display = "block";
			document.getElementById('errordiv').value = "Encryption error.";
			document.getElementById('status').style.display = "none";
		}
	});
}