#!/bin/bash

gcc -o filenuke filenuke.c

echo "
create database passwords;
grant all privileges on passwords.* to 'passman'@'localhost' identified by '';
use passwords;
create table cryptokeys (userhash CHAR(64), public VARCHAR(3000), private VARCHAR(3000));
create table algorithms (userhash CHAR(64), curve VARCHAR(16), aes VARCHAR(16));" > /tmp/setup.tmp

echo "Please input your mysql root password: "
mysql -u root -p < /tmp/setup.tmp
rm /tmp/setup.tmp
