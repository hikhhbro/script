#!/bin/bash
. /home/hik/private/script/base.sh
adb root
adb remount
adb disable-verity
adb shell echo  '1 > /sys/class/backlight/panel0-backlight/bl_power'