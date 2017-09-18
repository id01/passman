<?php
// Line 1: Challenge
// Line 2: Encrypted ECC Private Key
$passwordPort = 3000;
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
	$mytokenfile = "/tmp/passman_0.tmp";
	while (file_exists($mytokenfile))
	{
		$mytokenfile = "/tmp/passman_" . rand() . ".tmp";
	}
	$pfile = popen("nc localhost " . $passwordPort . " > " . $mytokenfile, "w");
	fwrite($pfile, "GETECC\n");
	fwrite($pfile, $_POST["userhash"] . "\n");
	pclose($pfile);
	echo file_get_contents($mytokenfile);
	unlink($mytokenfile);
}
?>
