#!/bin/bash
_describe() { echo "关闭mi11手机屏幕"; }
if [[ "${describe}" == "describe" ]];then _describe;exit 0;fi

adb root
adb remount
adb disable-verity
adb shell echo  '1 > /sys/class/backlight/panel0-backlight/bl_power'