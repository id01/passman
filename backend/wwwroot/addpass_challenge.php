<?php
// Line 1: Challenge
// Line 2: Encrypted ECC Private Key
if ($_POST["account"] == "" || $_POST["userhash"] == "")
{
        echo "Error: Username or Account Name not specified";
} else if (!ctype_xdigit($_POST["account"])) {
	echo "Account hash is malformed. Please try again.";
} else {
	// Start session, create challenge
	session_start();
	$_SESSION["account"] = $_POST["account"];
	$randFile = fopen("/dev/urandom", "r");
	$_SESSION["challenge"] = base64_encode(fread($randFile, 24));
	fclose($randFile);
	echo $_SESSION["challenge"]."\n";
	// Get ECC private key (encrypted) from server
	chdir(realpath("."));
	$sock = socket_create(AF_UNIX, SOCK_STREAM, 0);
	if (!$sock || !socket_connect($sock, "/tmp/passmansocket")) {
		echo "Internal Server Error.";
	} else {
		socket_write($sock, "GETECC\n");
		socket_write($sock, $_POST["userhash"] . "\n");
		echo socket_read($sock, 4096, PHP_BINARY_READ);
		socket_shutdown($sock);
	}
}
?>
