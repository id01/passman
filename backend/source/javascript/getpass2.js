// Submits getForm
function submitAction(event) {
	event.preventDefault();
	var notification = document.getElementById("notification");
	notification.className = "notification";
	notification.innerHTML = "Please wait...";
	var getForm = document.getElementById("getform");
	var userhash = simplehashuser(getForm.querySelector("[name=userin]").value.toLowerCase());
	jQuery.post(urllocation+"getpass.php", "userhash=" + userhash + "&account=" +
		simplehashaccount(getForm.querySelector("[name=account]").value.toLowerCase(), userhash), updateEncrypted, "text"
	).fail(function(){
		notification.className = "notification_failure";
		notification.innerHTML = "AJAX Error.";
	});
}
// Decrypts the response to submitAction and writes to decrypted.
function updateEncrypted(data) {
	// Get data for vars and activate CBC
	var passwd = document.getElementById("password_input").value;
	var notification = document.getElementById("notification");
	var encdata = data.split('\n')[0];
	// Check output
	if (encdata.substring(0, 6) == "VALID ")
	{
		// Try decryption. If it fails, there is an incorrect password.
		var encPassword = encdata.substring(6);
		try {
			document.getElementById("decrypted").value = str.fromBits(sjcldecrypt(b64.toBits(encPassword), passwd));
			document.getElementById("resultdiv").className = "resultdiv_visible";
			notification.className = "notification_success";
			notification.innerHTML = "Done.";
			if (document.location.search == "?extension") {
				copyAction();
			}
		} catch (err) {
			document.getElementById('notification').className = "notification_failure";
			document.getElementById('notification').innerHTML = "Incorrect Password.";
			return;
		}
	}
	else
	{
		notification.className = "notification_failure";
		notification.innerHTML = "Error getting entry: "+encdata;
	}
}
