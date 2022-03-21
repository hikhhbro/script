#!/bin/bash
. /home/hik/private/script/base.sh
adb root
adb remount
adb disable-verity
adb shell reboot -p