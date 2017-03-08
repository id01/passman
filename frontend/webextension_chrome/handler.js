var tabNumber;
var myPassword;

// All this does is logs in the console
function doStuff(response) {
	console.log(response);
	if (typeof(response) == "undefined") {
		myPassword = "ERR";
	}
	else if (response.indexOf("GOT PASSWORD: ") == 0) {
		myPassword = response.substring(14);
	}
	else if (response.indexOf("ADDED PASSWORD: ") == 0) {
		myPassword = response.substring(16);
	}
	else if (response.indexOf("INCORRECT") == 0) {
		myPassword = "WRONG";
	}
	else {
		myPassword = "ERR";
	}
	chrome.tabs.query({currentWindow: true, active: true}, function(tabArray) {
		tabNumber = tabArray[0].id;
		chrome.tabs.sendMessage(tabNumber, {password: myPassword});
	});
	console.log(response);
}

// Connect to foreground script
chrome.runtime.onMessage.addListener(function (userpass) {
	chrome.runtime.sendNativeMessage(
		"passman",
		{ text: userpass.user + "\n" + userpass.pass + "\n" + userpass.getadd + " " + userpass.host + "\n" },
		doStuff
	);
});