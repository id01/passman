create database passwords;
create user if not exists 'passman'@'localhost';
grant all privileges on passwords.* to 'passman'@'localhost' identified by '';
use passwords;
create table cryptokeys (userhash CHAR(32), public VARCHAR(128), private VARCHAR(256));
create table passwords (userhash CHAR(32), account CHAR(32), encrypted VARCHAR(180));