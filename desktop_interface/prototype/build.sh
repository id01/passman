#!/bin/sh

g++ -Wl,-rpath=libscrypt -O2 -fPIC -c -o prototype.o prototype.cpp
g++ -o prototype prototype.o -O2 -Llibscrypt -lscrypt -lcrypto -lssl -lcurl -lcryptopp -lpthread