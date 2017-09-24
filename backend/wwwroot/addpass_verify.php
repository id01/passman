<?php
if ($_POST["userhash"] == "" || $_POST["passwordcrypt"] == "" || $_POST["signature"] == "")
{
        echo "Something went wrong.";
} else {
	// Start session
	session_start();
	// Try adding password
	chdir(realpath("."));
	$sock = socket_create(AF_UNIX, SOCK_STREAM, 0);
	if (!$sock || !socket_connect($sock, "/tmp/passmansocket")) {
		echo "Internal Server Error.";
	} else {
		socket_write($sock, "ADDP\n");
		socket_write($sock, $_POST["userhash"] . "\n");
		socket_write($sock, $_SESSION["account"] . "\n");
		socket_write($sock, $_SESSION["challenge"] . "\n");
		socket_write($sock, $_POST["passwordcrypt"] . "\n");
		socket_write($sock, $_POST["signature"] . "\n");
		echo socket_read($sock, 4096, PHP_BINARY_READ);
		socket_shutdown($sock);
	}
}
?>
