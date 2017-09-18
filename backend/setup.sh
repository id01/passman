#!/bin/bash

echo "
create database passwords;
create user if not exists 'passman'@'localhost';
grant all privileges on passwords.* to 'passman'@'localhost' identified by '';
use passwords;
create table cryptokeys (userhash CHAR(32), public VARCHAR(256), private VARCHAR(512));" > /tmp/setup.tmp

echo "Please input your mysql root password: "
mysql -u root -p < /tmp/setup.tmp
rm /tmp/setup.tmp

echo "Done with basic setup."
