function submitAction(event) {
	event.preventDefault();
	var notification = document.getElementById("notification");
	notification.style.color = "";
	notification.innerHTML = "Please wait...";
	var getForm = document.getElementById("getform");
	jQuery.post("getpass.php", "userin=" + getForm.querySelector("[name=userin]").value + "&account=" + getForm.querySelector("[name=account]").value, updateEncrypted, "text");
}
function updateEncrypted(data) {
	var pass = document.getElementById("password_input").value;
	var notification = document.getElementById("notification");
	var keyHash = sjcl.hash.sha256.hash(pass);
	var datasplit = data.split("\n");
	var encdata = datasplit[0];
	var eccdata = datasplit[1];
	var aesdata = datasplit[2];
	sjcl.beware["CBC mode is dangerous because it doesn't protect message integrity."]();
	if (encdata.substring(0, 6) == "VALID ")
	{
	        var encPasswordHex = sjcl.codec.hex.fromBits(sjcl.codec.base64.toBits(encdata.substring(6)));
	        var encPassword = sjcl.codec.hex.toBits(encPasswordHex.substring(0, encPasswordHex.length-32-64));
	        var encPasswordHash = encPasswordHex.substring(encPasswordHex.length-64);
	        var encPasswordIv = sjcl.codec.hex.toBits(encPasswordHex.substring(encPasswordHex.length-32-64, encPasswordHex.length-64));
	        var aesParams = aesdata.split('-');
	        var aesBits = aesParams[1];
	        var aesMode = aesParams[2];
		if (aesMode == "cbc")
		{
			var decPassword;
			try {
	                	decPassword = sjcl.codec.utf8String.fromBits(sjcl.mode.cbc.decrypt(new sjcl.cipher.aes(keyHash), encPassword, encPasswordIv));
			}
			catch (err) {
				decPassword = "";
			}
	                if (encPasswordHash == sjcl.codec.hex.fromBits(sjcl.hash.sha256.hash(decPassword)))
	                {
				notification.style.color = "green";
				notification.innerHTML = "Done.";
	                        document.getElementById("decrypted").value = decPassword;
	                }
			else
			{
				notification.style.color = "red";
				notification.innerHTML = "Incorrect password.";
			}
	        }
	}
	else
	{
		notification.style.color = "red";
		notification.innerHTML = "Entry doesn't exist.";
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
