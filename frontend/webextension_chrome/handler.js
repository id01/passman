var tabNumber;
var myPassword;
var myMessage;

// Function to query server.
function queryServer(userpass) {
	var xhr = new XMLHttpRequest();
	xhr.open("POST", "http://localhost:13880/", true);
	xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xhr.onreadystatechange = function() {
		if (xhr.readyState == XMLHttpRequest.DONE && xhr.status == 200) {
			doStuff(xhr.responseText);
		} else {
			doStuff(null);
		}
	}
	xhr.send("PASSMAN+INPUT+IS="+encodeURIComponent(userpass.user)+"%0A"+encodeURIComponent(userpass.pass)+"%0A"+
		encodeURIComponent(userpass.getadd)+"%20"+encodeURIComponent(userpass.host));
}

// All this does is logs in the console
function doStuff(response) {
	console.log(response);
	if (typeof(response) == "undefined" || response === null) {
		myPassword = "\x02";
		myMessage = "Unknown Error.";
	} else if (response.split("\x04")[1].indexOf("Password: ") == 0) {
		var resSplit = response.split("\x04");
		myPassword = resSplit[1].substring(10);
		myMessage = resSplit[0];
	} else {
		var resSplit = response.split("\x04");
		myPassword = "\x02";
		myMessage = resSplit[1];
	}
	chrome.tabs.query({currentWindow: true, active: true}, function(tabArray) {
		tabNumber = tabArray[0].id;
		chrome.tabs.sendMessage(tabNumber, {password: myPassword, errMessage: myMessage});
	});
}

// Connect to foreground script
chrome.runtime.onMessage.addListener(queryServer);
