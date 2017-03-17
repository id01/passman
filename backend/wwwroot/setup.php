<?php
if ($_POST["key"] != $_POST["key2"])
{
	echo "The key and verification are different. Please try again.";
}
else
{
	switch ($_POST["curve"])
	{
		// Prime curves
		case 1: $curve = "secp224k1"; break;
		case 2: $curve = "secp224r1"; break;
		case 3: $curve = "secp521r1"; break;
		// Binary curves
		case 4: $curve = "sect283k1"; break;
		case 5: $curve = "sect283r1"; break;
		case 6: $curve = "sect571k1"; break;
		case 7: $curve = "sect571r1"; break;
		default: $curve = "";
	}
	switch ($_POST["aes"])
	{
		case 1: $aes = "aes-256-cbc"; break; // cbc cipher. Will probably add more in future.
		default: $aes = "";
	}
	if ($curve == "" || $aes == "")
	{
		echo "Something went wrong...";
	}
	else
	{
		$usermd5 = md5($_POST["username"]);
		$inputfile = fopen("/tmp/" . $usermd5, "w");
		exec("chmod 600 /tmp/" . $usermd5);
		fwrite($inputfile, $_POST["username"] . "\n");
		fwrite($inputfile, $_POST["key"] . "\n");
		fclose($inputfile);
		chdir(realpath("."));
		echo "Result: " . exec("python ../setup.py " . $curve . " " . $aes . " < /tmp/" . $usermd5 . " 2>&1");
		exec("../filenuke /tmp/" . $usermd5);
	}
}
?>
