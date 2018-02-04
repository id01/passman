// Optimize getElementById calls
function getElementById(name) {
	return document.getElementById(name);
}

// Global var for notification
var notif;
function initVars() {
	notif = getElementById("notification");
}

// Submits getForm
function submitAction(event) {
	event.preventDefault();
	notif.className = "notification";
	notif.innerHTML = "Please wait...";
	var getForm = getElementById("getform");
	var userhash = simplehashuser(getForm.querySelector("[name=userin]").value.toLowerCase());
	jQuery.post(urllocation+"getpass.php", "userhash=" + userhash + "&account=" +
		simplehashaccount(getForm.querySelector("[name=account]").value.toLowerCase(), userhash), updateEncrypted, "text"
	).fail(function(){
		notif.className = "notification_failure";
		notif.innerHTML = "AJAX Error.";
	});
}
// Decrypts the response to submitAction and writes to decrypted.
function updateEncrypted(data) {
	// Get data for vars and activate CBC
	var passwd = getElementById("password_input").value;
	var encdata = data.split('\n')[0];
	// Check output
	if (encdata.substring(0, 6) == "VALID ")
	{
		// Try decryption. If it fails, there is an incorrect password.
		var encPassword = encdata.substring(6);
		try {
			getElementById("decrypted").value = str.fromBits(sjcldecrypt(b64.toBits(encPassword), passwd));
			getElementById("resultdiv").className = "resultdiv_visible";
			notif.className = "notification_success";
			notif.innerHTML = "Done.";
			if (document.location.search == "?extension") {
				copyAction();
			}
		} catch (err) {
			notif.className = "notification_failure";
			notif.innerHTML = "Incorrect Password.";
			return;
		}
	}
	else
	{
		notif.className = "notification_failure";
		notif.innerHTML = "Error getting entry: "+encdata;
	}
}
