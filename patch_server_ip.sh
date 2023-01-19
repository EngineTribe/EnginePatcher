#!/bin/bash
echo "Patching server IP for $1"
sed -i "s/209.222.97.175:25019/103.90.161.247:30000/g" "$1"
