#!/bin/bash

echo "$HOME is your home directory"
# Get browser
echo "Configure for [1] Chrome or [2] Firefox?"
read browser
if [ "$browser" = "1" ]; then echo "Chrome Selected"
elif [ "$browser" = "2" ]; then echo "Firefox Selected"
else echo "Invalid Selection."; exit 1; fi
# Make directory
mkdir "$HOME/.passman" 2>/dev/null
# Create manifest file
head -n 3 manifest.json > /tmp/passman.json
echo "\"path\": \"$HOME/.passman/run.sh\"," >> /tmp/passman.json
echo "\"type\": \"stdio\"," >> /tmp/passman.json
# Allow extension for chrome or firefox
if [ "$browser" = "1" ]; then
	echo "Install the extension on Chrome, then paste the ID (obscure string of letters) here."
	read chromeid
	echo '"allowed_origins": [' >> /tmp/passman.json
	echo "\"chrome-extension://$chromeid/\"" >> /tmp/passman.json
	echo "]" >> /tmp/passman.json
else
	echo "\"allowed_extensions\": [" >> /tmp/passman.json
	echo "\"passman@127.0.0.1\"" >> /tmp/passman.json
	echo "]" >> /tmp/passman.json
fi
# End manifest file
echo "}" >> /tmp/passman.json
# Move manifest file over
if [ "$browser" = "1" ]; then
	echo "Is this [1] Chromium or [2] Google-Chrome?";
	read cog;
	if [ "$cog" = "2" ]; then
		mkdir "$HOME/.config/google-chrome/NativeMessagingHosts" 2>/dev/null
		mv "/tmp/passman.json" "$HOME/.config/google-chrome/NativeMessagingHosts/passman.json"
	else
		mkdir "$HOME/.config/chromium/NativeMessagingHosts" 2>/dev/null
		mv "/tmp/passman.json" "$HOME/.config/chromium/NativeMessagingHosts/passman.json"
	fi
else
	mv "/tmp/passman.json" "$HOME/.mozilla/native-messaging-hosts/passman.json"
fi
# Copy all other files
cp ./* "$HOME/.passman/"
# Construct run file
echo "#!/bin/sh" > "$HOME/.passman/run.sh"
echo "cd $HOME/.passman" >> "$HOME/.passman/run.sh"
echo "python passclient_webex.py" >> "$HOME/.passman/run.sh"
# Done! Ask the user to enable extension
echo "Done! Now if you haven't already, install and enable the extension!"
