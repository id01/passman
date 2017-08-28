// Construct frame and all inputs
var createframe = document.createElement("div");
createframe.id = "passmanframe";
createframe.style = "position:absolute; z-index:999; top:0; left:0; width:200; height:160; display:none; background-color:white";
createframe.innerHTML = "<span name='err'>Please Login</span>";
createframe.innerHTML += "<br>Username: ";
var createinput = document.createElement("input");
createinput.type = "text";
createinput.name = "passmanuser";
createframe.append(createinput);
createframe.innerHTML += "<br/>Password: ";
createinput = document.createElement("input");
createinput.type = "password";
createinput.name = "passmanpass";
createframe.append(createinput);
createframe.innerHTML += "<br/>Account name: ";
createinput = document.createElement("input");
createinput.type = "text";
createinput.name = "passmanname";
createframe.append(createinput);
createframe.innerHTML += "<br/>";
createinput = document.createElement("select");
createinput.name = "passmangetadd";
createinput.innerHTML = "<option value='GET'>Get password</select>";
createinput.innerHTML += "<option value='ADD 8'>Add password (8)</select>";
createinput.innerHTML += "<option value='ADD 15'>Add password (15)</select>";
createinput.innerHTML += "<option value='ADD 24'>Add password (24)</select>";
createinput.innerHTML += "<option value='ADD 31'>Add password (31)</select>";
createinput.innerHTML += "<option value='ADD 63'>Add password (63)</select>";
createframe.append(createinput);
createframe.innerHTML += "<br/>";
createinput = document.createElement("button");
createinput.type="button";
createinput.name="passmansubmit";
createinput.innerHTML = "Submit";
createframe.append(createinput);
document.body.appendChild(createframe);
var currentSelectPassword;

function isDescendant(parent, child) {
	var node = child.parentNode;
	while (node != null) {
		if (node == parent) {
			return true;	
		}
		node = node.parentNode;
	}
	return false;
}

function pmFormHandler() {
	document.getElementById("passmanframe").querySelector("[name=err]").style.color = "black";
	document.getElementById("passmanframe").querySelector("[name=err]").innerHTML = "Please Wait...";
	var user = document.getElementById("passmanframe").querySelectorAll("[name=passmanuser]")[0].value;
	var pass = document.getElementById("passmanframe").querySelectorAll("[name=passmanpass]")[0].value;
	var getadd = document.getElementById("passmanframe").querySelectorAll("[name=passmangetadd]")[0].value;
	var myHost = document.getElementById("passmanframe").querySelectorAll("[name=passmanname]")[0].value;
	chrome.runtime.sendMessage({"user": user, "pass": pass, "host": myHost, "getadd": getadd});
}

document.addEventListener('click', function (e) {
	var myFrame = document.getElementById("passmanframe");
	if (!isDescendant(myFrame, e.target))
	{
		if (e.target.type == "password")
		{
			var boundingRect = e.target.getBoundingClientRect();
			var elementLeft = boundingRect.left;
			var elementTop = boundingRect.top;
			var elementBottom = boundingRect.bottom;
			if (elementTop >= 180)
				myFrame.style.top = elementTop-180;
			else
				myFrame.style.top = elementBottom+20;
			myFrame.style.left = elementLeft;
			myFrame.style.display = "";
			currentSelectPassword = e.target;
		}
		else
		{
			myFrame.style.display = "none";
			myFrame.querySelector("[name=err]").style.color = "black";
			myFrame.querySelector("[name=err]").innerHTML = "Please Login";
		}
	}
	else if (e.target.name == "passmansubmit")
	{
		pmFormHandler();
	}
});

chrome.runtime.onMessage.addListener(request => {
	if (request.password.charCodeAt(0) == 2) {
		document.getElementById("passmanframe").querySelector("[name=err]").style.color = "red";
		document.getElementById("passmanframe").querySelector("[name=err]").innerHTML = request.errMessage;
	} else {
		document.getElementById("passmanframe").querySelector("[name=err]").style.color = "green";
		document.getElementById("passmanframe").querySelector("[name=err]").innerHTML = request.errMessage;
		currentSelectPassword.value = request.password;
	}
});
