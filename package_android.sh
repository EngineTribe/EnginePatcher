#!/bin/bash
7z x $1 $1.d
cp splash.png $1.d/assets/splash.png
rm $1.d/assets/font_as.ttf
cp libyoyo.so $1.d/lib/armeabi-v7a/libyoyo.so
cp fonts/fontcjk.ttf $1.d/res/fontcjk.ttf
7z a ${1/.apk/-patched.apk} ./$1.d/*
zipalign -f -v 4 ${1/.apk/-patched.apk} ${1/.apk/-patched-signed.apk}
apksigner sign --ks keystore/enginetribe.keystore --ks-key-alias EngineTribe ${1/.apk/-patched-signed.apk}
rm -rf $1.ds
