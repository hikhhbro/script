#!/bin/bash
_describe() { echo "关闭chroot mi 11"; }
if [[ "${describe}" == "describe" ]];then _describe;exit 0;fi
adb root
adb remount
adb disable-verity
adb shell reboot -p