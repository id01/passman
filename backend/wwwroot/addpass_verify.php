<?php
$passwordPort = 3000;
if ($_POST["userhash"] == "" || $_POST["passwordcrypt"] == "" || $_POST["signature"] == "")
{
        echo "Something went wrong.";
} else {
	// Start session
	session_start();
	// Try adding password
	chdir(realpath("."));
	$mytokenfile = "/tmp/passman_0.tmp";
	while (file_exists($mytokenfile))
	{
		$mytokenfile = "/tmp/passman_" . rand() . ".tmp";
	}
	$pfile = popen("nc localhost " . $passwordPort . " > " . $mytokenfile, "w");
	fwrite($pfile, "ADDP\n");
	fwrite($pfile, $_POST["userhash"] . "\n");
	fwrite($pfile, $_SESSION["account"] . "\n");
	fwrite($pfile, $_SESSION["challenge"] . "\n");
	fwrite($pfile, $_POST["passwordcrypt"] . "\n");
	fwrite($pfile, $_POST["signature"] . "\n");
	pclose($pfile);
	echo file_get_contents($mytokenfile);
	unlink($mytokenfile);
}
?>
