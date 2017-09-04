<?php
$passHash = "stuff"; // Replace this with sha256 hash of password
if (hash('sha256', $_POST["auth"]) != $passHash) {
	sleep(1);
	echo "Server password incorrect.";
} else if ($_POST["key"] != $_POST["key2"]) {
	echo "The key and verification are different. Please try again.";
} else {
	if ($_POST["key"] == "" || $_POST["username"] == "") {
		echo "Username or key cannot be blank!";
	} else {
		$usermd5 = md5($_POST["username"]);
		$inputfile = fopen("/tmp/" . $usermd5, "w");
		exec("chmod 600 /tmp/" . $usermd5);
		fwrite($inputfile, $_POST["username"] . "\n");
		fwrite($inputfile, $_POST["key"] . "\n");
		fclose($inputfile);
		chdir(realpath("."));
		echo "Result: " . exec("python ../setup.py < /tmp/" . $usermd5 . " 2>&1");
		exec("srm /tmp/" . $usermd5);
	}
}
?>
