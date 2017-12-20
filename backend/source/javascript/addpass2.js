// Global vars for challengeForm, verifyForm, and notification.
var cForm, vForm, notif;
function initVars() {
	notif = document.getElementById("notification");
	cForm = document.getElementById("challengeform");
	vForm = document.getElementById("verifyform");
}

// Handler for an AJAX Error
function ajaxError() {
	notif.className = "notification_failure";
	notif.innerHTML = "AJAX Error.";
}

// Submits the challenge form
function challengeSubmitAction(event) {
	event.preventDefault();
	notif.className = "notification";
	notif.innerHTML = "Please wait...";
	var userhash = simplehashuser(cForm.querySelector("[name=userin]").value.toLowerCase());
	cForm.querySelector("[name=userhash]").value = userhash;
	vForm.querySelector("[name=accounthash]").value = simplehashaccount(cForm.querySelector("[name=account]").value.toLowerCase(), userhash);
	jQuery.post(urllocation+"addpass_challenge.php", "userhash=" + cForm.querySelector("[name=userhash]").value +
		"&account=" + vForm.querySelector("[name=accounthash]").value, buildVerifyForm, "text"
	).fail(ajaxError);
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
	vForm.querySelector("[name=userhash]").value = cForm.querySelector("[name=userhash]").value;
	// Parse data
	var dataSplit = data.trim('\n').split('\n');
	vForm.querySelector("[name=challenge]").value = dataSplit[0];
	// Check if error occured
	if (dataSplit.length != 3) {
		notif.className = "notification_failure";
		if (dataSplit.length == 0) {
			notif.innerHTML = "Unknown Error.";
		} else {
			notif.innerHTML = dataSplit[0];
		}
		return;
	}
	if (!dataSplit[1].startsWith("VALID")) {
		notif.className = "notification_failure";
		notif.innerHTML = dataSplit[1];
		return;
	}
	if (!dataSplit[2].startsWith("VALID")) {
		notif.className = "notification_failure";
		notif.innerHTML = dataSplit[2];
		return;
	}
	// Decrypt Secrets
	notif.innerHTML += ' <span id="notif_text">Decrypting Secrets...</span><span id="notif_status"></span>';
	setTimeout(function() {
		try {
			var passwd = document.getElementById('password_input').value;
			document.getElementById('ecckey').value = b64.fromBits(sjcldecrypt(b64.toBits(dataSplit[1].substring(6)), passwd));
		} catch (err) {
			notif.className = "notification_failure";
			notif.innerHTML = "Incorrect Password.";
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
				sig.updateString(dataSplit[2].substring(6)+'$'+
					vForm.querySelector("[name=userhash]").value+'$'+
					vForm.querySelector("[name=accounthash]").value+'$'+
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
	jQuery.post(urllocation+"addpass_verify.php", "userhash=" + vForm.querySelector("[name=userhash]").value +
	            "&account=" + vForm.querySelector("[name=accounthash]").value +
	            "&challenge=" + vForm.querySelector("[name=challenge]").value.replace(/\+/g, '%2B') +
	            "&passwordcrypt=" + vForm.querySelector("[name=passwordcrypt]").value.replace(/\+/g, '%2B') +
	            "&signature=" + vForm.querySelector("[name=signature]").value.replace(/\+/g, '%2B'), printVerifyResult, "text").fail(ajaxError);
}
// Prints the result of the verifyForm submission.
function printVerifyResult(data) {
	notif.className = "notification_failure";
	if (data.startsWith("Password already exists!") || data.startsWith("Invalid Signature") || data.startsWith("Password too long")) {
		notif.innerHTML = "Result: " + data;
	} else if (data == "") {
		notif.innerHTML = "Unknown Error.";
	} else {
		document.getElementById("resultdiv").className = "resultdiv_visible";
		notif.className = "notification_success";
		notif.innerHTML = "Result: " + data;
		if (document.location.search == "?extension" && data == "Success!") {
			copyAction();
		}
	}
}
