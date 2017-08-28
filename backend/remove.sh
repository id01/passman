#!/bin/sh

echo "This script removes a user. Input username below."
read REMOVEUSER
RUHASH=$(echo -n "$REMOVEUSER" | sha256sum | cut -d ' ' -f 1)
echo "use passwords;" > /tmp/remove.sql
echo "delete from cryptokeys where userhash='$RUHASH';" >> /tmp/remove.sql
echo "drop table $RUHASH;" >> /tmp/remove.sql
mysql -u passman < /tmp/remove.sql
rm /tmp/remove.sql
