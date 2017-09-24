// Submits getForm
function submitAction(event) {
	event.preventDefault();
	var notification = document.getElementById("notification");
	notification.style.color = "";
	notification.innerHTML = "Please wait...";
	var getForm = document.getElementById("getform");
	var userhash = md5(getForm.querySelector("[name=userin]").value.toLowerCase());
	jQuery.post(urllocation+"getpass.php", "userhash=" + userhash + "&account=" + md5(getForm.querySelector("[name=account]").value.toLowerCase()), updateEncrypted, "text");
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
			notification.style.color = "green";
			notification.innerHTML = "Done.";
		} catch (err) {
			document.getElementById('notification').style.color = "red";
			document.getElementById('notification').innerHTML = "Incorrect Password.";
			return;
		}
	}
	else
	{
		notification.style.color = "red";
		notification.innerHTML = "Error getting entry: "+encdata;
	}
}
// Copies the decrypted password.
function copyAction() {
        var decrypted = document.getElementById("decrypted");
        decrypted.disabled = "";
	decrypted.type = "text";
        decrypted.select();
        document.execCommand("copy");
	decrypted.type = "password";
        decrypted.disabled = "true";
}
