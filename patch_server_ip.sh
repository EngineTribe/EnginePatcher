#!/bin/bash
sha512sum "$1"
echo "Patching server IP for $1"
sed -i "s/209.222.97.175/enginetribe.gq/g" "$1"
sha512sum "$1"
