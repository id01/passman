<?php
$passHash = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"; // Replace this with sha256 hash of password
if (hash('sha256', $_POST["auth"]) != $passHash) {
	sleep(1);
	echo "Server password incorrect.";
} else {
/*	$inputfile = fopen("/tmp/" . $_POST["userhash"], "w");
	fwrite($inputfile, $_POST["userhash"] . "\n");
	fwrite($inputfile, $_POST["public"] . "\n");
	fwrite($inputfile, $_POST["encryptedprivate"] . "\n");
	fclose($inputfile);
	chdir(realpath("."));
	echo "Result: " . exec("python ../setup.py < /tmp/" . $_POST["userhash"] . " 2>&1");
	unlink("/tmp/" . $_POST["userhash"]);*/
	$sock = socket_create(AF_UNIX, SOCK_STREAM, 0);
	if (!$sock || !socket_connect($sock, "/tmp/passmansocket")) {
		echo "Internal Server Error.";
	} else {
		socket_write($sock, "SETUP\n");
		socket_write($sock, $_POST["userhash"] . "\n");
		socket_write($sock, $_POST["public"] . "\n");
		socket_write($sock, $_POST["encryptedprivate"] . "\n");
		echo socket_read($sock, 4096, PHP_BINARY_READ);
		socket_shutdown($sock);
	}
}
?>
