function updateStatus(statusObject) {
	var statusSpan = document.getElementById("notif_status");
	statusSpan.innerHTML = statusObject.what + ' - ' + (statusObject.i/statusObject.total) + '...';
}
function challengeSubmitAction(event) {
	event.preventDefault();
	var notification = document.getElementById("notification");
	notification.style.color = "";
	notification.innerHTML = "Please wait...";
	var cForm = document.getElementById("challengeform");
	cForm.querySelector("[name=userhash]").value = md5(cForm.querySelector("[name=userin]").value);
	jQuery.post("addpass_challenge.php", "userhash=" + cForm.querySelector("[name=userhash]").value + "&account=" + md5(cForm.querySelector("[name=account]").value), buildVerifyForm, "text");
}
function makePassword() {
	var text = "";
	var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.!";
	for (var i = 0; i < document.getElementById('plength').value; i++)
		text += possible.charAt(Math.floor(Math.random() * possible.length));
	return text;
}
function buildVerifyForm(data) {
	var userpass = document.getElementById("password_input").value;
	// Copy username
	document.getElementById("verifyform").querySelector("[name=userhash]").value = document.getElementById("challengeform").querySelector("[name=userhash]").value;
	// Parse data
	var dataSplit = data.split('\n');
	document.getElementById("challenge").value = dataSplit[0];
	// Check if error occured
	if (!dataSplit[1].startsWith("VALID")) {
		document.getElementById('notification').style.color = "red";
		document.getElementById('notification').innerHTML = dataSplit[1];
		return;
	}
	// Encrypt
	document.getElementById('notification').innerHTML += ' <span id="notif_text">Decrypting Secrets...</span><span id="notif_status"></span>';
	triplesec.decrypt({
		data: new triplesec.Buffer(dataSplit[1].substring(6), 'base64'),
		key: new triplesec.Buffer(document.getElementById('password_input').value),
		progress_hook: updateStatus
	}, function (wrongkey, ecckeybuf) {
		if (!wrongkey) {
			document.getElementById('ecckey').value = ecckeybuf.toString('hex');
			document.getElementById('notif_text').innerHTML = "Encrypting Password...";
			document.getElementById('decrypted').value = makePassword();
			// Generate and encrypt password
			triplesec.encrypt({
				data: new triplesec.Buffer(document.getElementById('decrypted').value),
				key: new triplesec.Buffer(document.getElementById('password_input').value),
				progress_hook: updateStatus
			}, function (err, buff) {
				if (!err) {
					document.getElementById('encryptedpass').value = buff.toString('base64');
					document.getElementById('notif_text').innerHTML = "Signing... ";
					// Sign everything
					var privateKeyHex = document.getElementById('ecckey').value;
					var sig = new KJUR.crypto.Signature({"alg": "SHA256withECDSA"});
					sig.init({d: privateKeyHex, curve: "secp256k1"});
					sig.updateString(document.getElementById("challenge").value+'$'+
						md5(document.getElementById('account_input').value)+'$'+
						document.getElementById('encryptedpass').value);
					var sighex = sig.sign();
					var sigb64 = btoa(sighex.match(/\w{2}/g).map(function(a){return String.fromCharCode(parseInt(a, 16));} ).join(""));
					document.getElementById("signature").value = sigb64;
					verifySubmitAction();
				} else {
					document.getElementById('notification').style.color = "red";
					document.getElementById('notification').innerHTML = "Encryption Error: "+err;
				}
			});
		} else {
			document.getElementById('notification').style.color = "red";
			document.getElementById('notification').innerHTML = "Incorrect Password.";
		}
	});
}
function verifySubmitAction() {
	var vForm = document.getElementById("verifyform");
	jQuery.post("addpass_verify.php", "userhash=" + vForm.querySelector("[name=userhash]").value +
	            "&passwordcrypt=" + vForm.querySelector("[name=passwordcrypt]").value.replace(/\+/g, '%2B') +
	            "&signature=" + vForm.querySelector("[name=signature]").value.replace(/\+/g, '%2B'), printVerifyResult, "text");
}
function printVerifyResult(data) {
	var notification = document.getElementById("notification");
	notification.style.color = "red";
	if (data.startsWith("Password already exists!") || data.startsWith("Invalid Signature")) {
		notification.innerHTML = "Result: " + data;
	} else if (data == "") {
		notification.innerHTML = "Unknown Error.";
	} else {
		notification.style.color = "green";
		notification.innerHTML = "Result: " + data;
	}
}
function copyAction() {
}
