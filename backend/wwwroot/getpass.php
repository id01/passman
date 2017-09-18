<?php
// This literally just returns the encrypted password
if ($_POST["account"] == "" || $_POST["userhash"] == "")
{
        echo "You need to specify both an account name and a user.";
} else if (!ctype_xdigit($_POST["account"])) {
	echo "Account hash is malformed. Please try again.";
} else {
	chdir(realpath("."));
	$mytokenfile = "/tmp/passman_0.tmp";
	while (file_exists($mytokenfile))
	{
		$mytokenfile = "/tmp/passman_" . rand() . ".tmp";
	}
	$pfile = popen("nc localhost 3000 > " . $mytokenfile, "w"); // This port must be changed along with that in passwordservice.py
	fwrite($pfile, "GET\n");
	fwrite($pfile, $_POST["userhash"] . "\n");
	fwrite($pfile, $_POST["account"] . "\n");
	pclose($pfile);
	echo file_get_contents($mytokenfile);
	unlink($mytokenfile);
}
?>
