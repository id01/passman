function updateStatus(statusObject) {
	var statusSpan = document.getElementById("notif_status");
	statusSpan.innerHTML = statusObject.what + ' - ' + (Math.ceil(1000*statusObject.i/statusObject.total)/10) + '...';
}
function submitAction(event) {
	event.preventDefault();
	var notification = document.getElementById("notification");
	notification.style.color = "";
	notification.innerHTML = "Please wait...";
	var getForm = document.getElementById("getform");
	var userhash = md5(getForm.querySelector("[name=userin]").value);
	jQuery.post("getpass.php", "userhash=" + userhash + "&account=" + md5(getForm.querySelector("[name=account]").value), updateEncrypted, "text");
}
function updateEncrypted(data) {
	// Get data for vars and activate CBC
	var pass = document.getElementById("password_input").value;
	var notification = document.getElementById("notification");
	var encdata = data.split('\n')[0];
	// Check output
	if (encdata.substring(0, 6) == "VALID ")
	{
		// Try decryption. If it fails, there is an incorrect password.
		var encPassword = encdata.substring(6);
		var decPassword;
		document.getElementById('notification').innerHTML += ' <span id="notif_status"></span>';
		triplesec.decrypt({
			data: new triplesec.Buffer(encPassword, "base64"),
			key: new triplesec.Buffer(pass),
			progress_hook: updateStatus
		}, function (err, buff) {
			if (!err) {
				decPassword = buff.toString();
				notification.style.color = "green";
				notification.innerHTML = "Done.";
				document.getElementById("decrypted").value = decPassword;
			} else {
				notification.style.color = "red";
				notification.innerHTML = "Incorrect password.";
				console.log(err);
			}
		});
	}
	else
	{
		notification.style.color = "red";
		notification.innerHTML = "Error getting entry: "+encdata;
	}
}
function copyAction() {
        var decrypted = document.getElementById("decrypted");
        decrypted.disabled = "";
	decrypted.type = "text";
        decrypted.select();
        document.execCommand("copy");
	decrypted.type = "password";
        decrypted.disabled = "true";
}
