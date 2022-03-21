#!/bin/bash
_describe() { echo "推送sensor相关库到手机,默认推送libsensor.so 和libsensorservice.so 传入参数可推送 /system/lib/和/system/lib64/下的库"; }
if [[ "${describe}" == "describe" ]];then _describe;exit 0;fi

DIRPATH="/home/hik/ws/android/out/target/product/venus"
if [[ "$1" == "" ]];then
  adb push ${DIRPATH}/system/lib/libsensor.so /system/lib/
  adb push ${DIRPATH}/system/lib64/libsensor.so /system/lib64/

  adb push ${DIRPATH}/system/lib/libsensorservice.so /system/lib/
  adb push ${DIRPATH}/system/lib64/libsensorservice.so /system/lib64/
else
  for target_so in $*;do
    adb push ${DIRPATH}/system/lib/${target_so} /system/lib/
    adb push ${DIRPATH}/system/lib64/${target_so} /system/lib64/
  done
fi