#!/bin/sh

if [ "$1" = "" ]; then
	echo "Usage: ./backup.sh [backup directory]"
	exit 254
fi

OUTFL="$1/passbak_`date +%d_%m_%y`.sql"
echo "Backing up database passwords to $OUTFL..."
mysqldump -u passman passwords > "$OUTFL"
echo "Removing old backups (10 days or older)..."
find "$1" -type f -mtime +10 -name '*.sql' -execdir rm -- {} \;
