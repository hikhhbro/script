#!/bin/bash
_describe() { echo "编译安卓, 不带参数编译全部, 带模块名参数,-m使用make, 否则使用quickbuild"; }
if [[ "${describe}" == "describe" ]];then _describe;exit 0;fi

quickbuild () {
  ninja_bin="$ANDROID_BUILD_TOP/prebuilts/build-tools/linux-x86/bin/ninja"
  ninja_build_file="$ANDROID_BUILD_TOP/out/combined-$TARGET_PRODUCT.ninja"
  if [ ! -f $ninja_build_file ]; then
    echo "can't find ninja build file $ninja_build_file"
    make -j16 $1
    exit 0
  fi
  if [ ! -f $ninja_bin ]; then
    echo "can't find ninja binary $ninja_bin"
    make -j16 $1
    exit 0
  fi
  $ninja_bin -f $ninja_build_file $1
}
ORGDIR=$(pwd)
cd /home/hik/ws/android/
source build/envsetup.sh
lunch venus-userdebug
if [[ "$1" == "" ]];then
  ./mibuild.sh dist -j16 | tee build_full.log
  ./device/xiaomi/venus/flash_scripts/build_all.sh

elif  [[ "$1" == "-m" ]];then
    make -j16 $2
else 
  quickbuild $1
fi

cd $ORGDIR