#!/bin/bash
echo "Patching server IP for $1"
sed -i "s/http:\/\/103.195.101.206:25750/https:\/\/juego.enginetribe.gq/g" "$1"
