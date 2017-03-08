#!/bin/sh

stdbuf -oL tcpserver 0 3000 python /home/pi/passman/source/backend/passwords.py
