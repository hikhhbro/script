#!/bin/bash
. /home/hik/private/script/base.sh
DIRPATH="/home/hik/ws/android/out/target/product/venus"
if [[ "$1" == "" ]];then
  adb push ${DIRPATH}/system/lib/libsensor.so /system/lib/
  adb push ${DIRPATH}/system/lib64/libsensor.so /system/lib64/

  adb push ${DIRPATH}/system/lib/libsensorservice.so /system/lib/
  adb push ${DIRPATH}/system/lib64/libsensorservice.so /system/lib64/
else
  for target_so in $*;do
    adb push ${DIRPATH}/system/lib/${target_so} /system/lib/
  done
fi