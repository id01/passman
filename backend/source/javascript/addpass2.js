// Optimize getElementById calls
function getElementById(name) {
	return document.getElementById(name);
}

// Global vars for challengeForm, verifyForm, notification, typeButton, password types, and password names.
var cForm, vForm, notif, typeButton, passTypes, passNames;
function initVars() {
	notif = getElementById("notification");
	cForm = getElementById("challengeform");
	vForm = getElementById("verifyform");
	typeButton = getElementById("typebutton");
	passTypes = ["A1#a", "b\\6\\4", "Aa1", "1\\2\\3", "Aa\\B", "a\\b\\c", "\\h\\ex"]; // Password types. Note that only the first 3 chars will be shown. '\\' is an escape sequence
	passNames = ["Alphanumeric with symbols", "64 possible characters", "Alphanumeric", "Digits only", "Uppercase and lowercase letters", "Lowercase letters only", "Hex digits"];
}

// Optimization functions for querySelector for names from cForm and vForm
function cFormQuerySelectName(name) {
	return cForm.querySelector("[name="+name+"]");
}
function vFormQuerySelectName(name) {
	return vForm.querySelector("[name="+name+"]");
}

// Handler for an AJAX Error
function ajaxError() {
	notif.className = "notification_failure";
	notif.innerHTML = "AJAX Error.";
}

// Called by typeButton to change the password type.
function typeChangeAction() {
	var newValue = (parseInt(typeButton.getAttribute("value")) + 1) % passTypes.length;
	typeButton.setAttribute("value", newValue);
	typeButton.innerHTML = passTypes[newValue].replace(/\\/g, '').substr(0, 3);
	typeButton.setAttribute("title", passNames[newValue]);
}

// Submits the challenge form
function challengeSubmitAction(event) {
	event.preventDefault();
	notif.className = "notification";
	notif.innerHTML = "Please wait...";
	var userhash = simplehashuser(cFormQuerySelectName("userin").value.toLowerCase());
	cFormQuerySelectName("userhash").value = userhash;
	vFormQuerySelectName("accounthash").value = simplehashaccount(cFormQuerySelectName("account").value.toLowerCase(), userhash);
	jQuery.post(urllocation+"addpass_challenge.php", "userhash=" + cFormQuerySelectName("userhash").value +
		"&account=" + vFormQuerySelectName("accounthash").value, buildVerifyForm, "text"
	).fail(ajaxError);
}
// Function to generate a password
function makePass() {
//	var text = prompt("Enter pass: ", ""); // Uncomment to import passwords
	// Define constants
	var lowercase = "abcdefghijklmnopqrstuvwxyz"; // Lowercase letters. Symbolized by 'a'
	var uppercase = lowercase.toUpperCase(); // Uppercase letters. Symbolized by 'A'
	var digits = "0123456789"; // Digits. Symbolized by '1'
	var hexdigits = digits+"abcdef"; // Hex digits. Symbolized by 'x'
	var b64digits = lowercase+uppercase+".!"; // Base64 digits. Symbolized by 'b'
	var symbol14 = ".,!@#$%^&*-_+="; // 14 symbols. Symbolized by '#'
	// Build passwordChars to specification of user
	var passwordChars = "";
	var typeButtonValue = parseInt(typeButton.getAttribute("value")); // Get numerical type button value
	var selectedpType = passTypes[typeButtonValue].replace(/\\./g, '_'); // Password type selected. Replace escaped things with an underscore (dummy character).
	for (var i = 0; i < selectedpType.length; i++) { // Iterate through selectedpType first 3 letters
		switch (selectedpType.charCodeAt(i)) {
			case 35: passwordChars += symbol14; break; // '#'
			case 49: passwordChars += digits; break; // '1'
			case 65: passwordChars += uppercase; break; // 'A'
			case 97: passwordChars += lowercase; break; // 'a'
			case 98: passwordChars += b64digits; break; // 'b'
			case 120: passwordChars += hexdigits; break; // 'x'
		}
	}
	// Generate password
	var plength = parseInt(getElementById('plength').value) || 15;
	var choices = new Uint32Array(plength); window.crypto.getRandomValues(choices);
	var textArray = new Uint8Array(plength);
	for (var i = 0; i < plength; i++) {
		textArray[i] = passwordChars.charCodeAt(choices[i] % passwordChars.length);
	}
	return new TextDecoder("ascii").decode(textArray);
}
// Called by challengeSubmitAction. Builds the verifyForm input
function buildVerifyForm(data) {
	// Copy username
	vFormQuerySelectName("userhash").value = cFormQuerySelectName("userhash").value;
	// Parse data
	var dataSplit = data.trim('\n').split('\n');
	vFormQuerySelectName("challenge").value = dataSplit[0];
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
			var passwd = getElementById('password_input').value;
			getElementById('ecckey').value = b64.fromBits(sjcldecrypt(b64.toBits(dataSplit[1].substring(6)), passwd));
		} catch (err) {
			notif.className = "notification_failure";
			notif.innerHTML = "Incorrect Password.";
			return;
		}
		// Encrypt Password
		getElementById('notif_text').innerHTML = "Encrypting Password...";
		setTimeout(function() {
			getElementById('decrypted').value = makePass();
			getElementById('encryptedpass').value = b64.fromBits(sjclencrypt(str.toBits(getElementById('decrypted').value), passwd));
			// Sign everything
			getElementById('notif_text').innerHTML = "Signing... ";
			setTimeout(function() {
				var prvKeyB64 = getElementById('ecckey').value;
				var sig = new KJUR.crypto.Signature({"alg": "SHA256withECDSA"});
				sig.init('-----BEGIN PRIVATE KEY-----'+prvKeyB64+'-----END PRIVATE KEY-----');
				sig.updateString(dataSplit[2].substring(6)+'$'+
					vFormQuerySelectName("userhash").value+'$'+
					vFormQuerySelectName("accounthash").value+'$'+
					getElementById('encryptedpass').value);
				var sighexder = sig.sign();
				var sighex = KJUR.crypto.ECDSA.asn1SigToConcatSig(sighexder);
				var sigb64 = btoa(sighex.match(/\w{2}/g).map(function(a){return String.fromCharCode(parseInt(a, 16));} ).join(""));
				getElementById("signature").value = sigb64;
				setTimeout(verifySubmitAction, 20);
			}, 20);
		}, 20);
	}, 20);
}
// Called by buildVerifyForm. Submits the verifyForm.
function verifySubmitAction() {
	jQuery.post(urllocation+"addpass_verify.php", "userhash=" + vFormQuerySelectName("userhash").value +
	            "&account=" + vFormQuerySelectName("accounthash").value +
	            "&challenge=" + vFormQuerySelectName("challenge").value.replace(/\+/g, '%2B') +
	            "&passwordcrypt=" + vFormQuerySelectName("passwordcrypt").value.replace(/\+/g, '%2B') +
	            "&signature=" + vFormQuerySelectName("signature").value.replace(/\+/g, '%2B'), printVerifyResult, "text").fail(ajaxError);
}
// Prints the result of the verifyForm submission.
function printVerifyResult(data) {
	notif.className = "notification_failure";
	if (data.startsWith("Password already exists!") || data.startsWith("Invalid Signature") || data.startsWith("Password too long")) {
		notif.innerHTML = "Result: " + data;
	} else if (data == "") {
		notif.innerHTML = "Unknown Error.";
	} else {
		getElementById("resultdiv").className = "resultdiv_visible";
		notif.className = "notification_success";
		notif.innerHTML = "Result: " + data;
		if (document.location.search == "?extension" && data == "Success!") {
			copyAction();
		}
	}
}