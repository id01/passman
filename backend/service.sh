#!/bin/sh

stdbuf -oL tcpserver 0 3000 python "`dirname $0`/passwords.py"
