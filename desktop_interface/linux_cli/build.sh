#!/bin/sh

g++ -c ../main/main.cpp -O2 -Llibscrypt -lscrypt -lcrypto -lssl -lcurl -lcryptopp -o ../main/main.o
g++ cli.cpp ../main/main.o -O2 -Llibscrypt -lscrypt -lcrypto -lssl -lcurl -lcryptopp -o cli