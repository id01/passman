// Submits the challenge form
function challengeSubmitAction(event) {
	event.preventDefault();
	var notification = document.getElementById("notification");
	notification.className = "notification";
	notification.innerHTML = "Please wait...";
	var cForm = document.getElementById("challengeform");
	cForm.querySelector("[name=userhash]").value = md5(cForm.querySelector("[name=userin]").value.toLowerCase());
	jQuery.post(urllocation+"addpass_challenge.php", "userhash=" + cForm.querySelector("[name=userhash]").value + "&account=" + md5(cForm.querySelector("[name=account]").value.toLowerCase()), buildVerifyForm, "text");
}
// Function to generate a password
function makePassword() {
//	var text = prompt("Enter pass: ", ""); // Uncomment to import passwords
	var text = "";
	var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.!";
	var choice = new Uint8Array(1);
	for (var i = 0; i < document.getElementById('plength').value; i++) {
		window.crypto.getRandomValues(choice);
		text += possible.charAt(choice[0] >> 2);
	}
	return text;
}
// Called by challengeSubmitAction. Builds the verifyForm input
function buildVerifyForm(data) {
	// Copy username
	document.getElementById("verifyform").querySelector("[name=userhash]").value = document.getElementById("challengeform").querySelector("[name=userhash]").value;
	// Parse data
	var dataSplit = data.split('\n');
	document.getElementById("challenge").value = dataSplit[0];
	// Check if error occured
	if (!dataSplit[1].startsWith("VALID")) {
		document.getElementById('notification').className = "notification_failure";
		document.getElementById('notification').innerHTML = dataSplit[1];
		return;
	}
	// Decrypt Secrets
	document.getElementById('notification').innerHTML += ' <span id="notif_text">Decrypting Secrets...</span><span id="notif_status"></span>';
	setTimeout(function() {
		try {
			var passwd = document.getElementById('password_input').value;
			document.getElementById('ecckey').value = b64.fromBits(sjcldecrypt(b64.toBits(dataSplit[1].substring(6)), passwd));
		} catch (err) {
			document.getElementById('notification').className = "notification_failure";
			document.getElementById('notification').innerHTML = "Incorrect Password.";
			return;
		}
		// Encrypt Password
		document.getElementById('notif_text').innerHTML = "Encrypting Password...";
		setTimeout(function() {
			document.getElementById('decrypted').value = makePassword();
			document.getElementById('encryptedpass').value = b64.fromBits(sjclencrypt(str.toBits(document.getElementById('decrypted').value), passwd));
			// Sign everything
			document.getElementById('notif_text').innerHTML = "Signing... ";
			setTimeout(function() {
				var prvKeyB64 = document.getElementById('ecckey').value;
				var sig = new KJUR.crypto.Signature({"alg": "SHA256withECDSA"});
				sig.init('-----BEGIN PRIVATE KEY-----'+prvKeyB64+'-----END PRIVATE KEY-----');
				sig.updateString(document.getElementById("challenge").value+'$'+
					md5(document.getElementById('account_input').value.toLowerCase())+'$'+
					document.getElementById('encryptedpass').value);
				var sighexder = sig.sign();
				var sighex = KJUR.crypto.ECDSA.asn1SigToConcatSig(sighexder);
				var sigb64 = btoa(sighex.match(/\w{2}/g).map(function(a){return String.fromCharCode(parseInt(a, 16));} ).join(""));
				document.getElementById("signature").value = sigb64;
				setTimeout(verifySubmitAction, 20);
			}, 20);
		}, 20);
	}, 20);
}
// Called by buildVerifyForm. Submits the verifyForm.
function verifySubmitAction() {
	var vForm = document.getElementById("verifyform");
	jQuery.post(urllocation+"addpass_verify.php", "userhash=" + vForm.querySelector("[name=userhash]").value +
	            "&passwordcrypt=" + vForm.querySelector("[name=passwordcrypt]").value.replace(/\+/g, '%2B') +
	            "&signature=" + vForm.querySelector("[name=signature]").value.replace(/\+/g, '%2B'), printVerifyResult, "text");
}
// Prints the result of the verifyForm submission.
function printVerifyResult(data) {
	var notification = document.getElementById("notification");
	notification.className = "notification_failure";
	if (data.startsWith("Password already exists!") || data.startsWith("Invalid Signature")) {
		notification.innerHTML = "Result: " + data;
	} else if (data == "") {
		notification.innerHTML = "Unknown Error.";
	} else {
		document.getElementById("resultdiv").className = "resultdiv_visible";
		notification.className = "notification_success";
		notification.innerHTML = "Result: " + data;
		if (document.location.search == "?extension" && data == "Success!") {
			copyAction();
		}
	}
}
