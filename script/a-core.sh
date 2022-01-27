#!/bin/bash
. /home/hik/private/script/base.sh

cd /home/hik/minacore/andriod/
_task ./build/build.py build -C out android-compat

read

_task cd /home/hik/minacore/andriod/out/lib/
_task adb push * /mina/mina/lib/
read
_task cd /home/hik/minacore/andriod/out/lib/libegl/
_task adb push * /mina/mina/lib/libegl/
read
_task cd /home/hik/minacore/andriod/out/lib/libhybris/linker/
_task adb push * /mina/mina/lib/libhybris/linker/
read
_task cd /home/hik/minacore/andriod/out/android/lib/
_task adb push * /mina/mina/android/lib/