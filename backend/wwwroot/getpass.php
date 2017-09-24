<?php
// This literally just returns the encrypted password
if ($_POST["account"] == "" || $_POST["userhash"] == "")
{
        echo "You need to specify both an account name and a user.";
} else if (!ctype_xdigit($_POST["account"])) {
	echo "Account hash is malformed. Please try again.";
} else {
	chdir(realpath("."));
	$sock = socket_create(AF_UNIX, SOCK_STREAM, 0);
	if (!$sock || !socket_connect($sock, "/tmp/passmansocket")) {
		echo "Internal Server Error.";
	} else {
		socket_write($sock, "GET\n");
		socket_write($sock, $_POST["userhash"] . "\n");
		socket_write($sock, $_POST["account"] . "\n");
		echo socket_read($sock, 4096, PHP_BINARY_READ);
		socket_shutdown($sock);
	}
}
?>
