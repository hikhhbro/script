#!/bin/bash
source build/envsetup.sh
lunch venus-userdebug
./mibuild.sh dist -j16 | tee build_full.log
./device/xiaomi/venus/flash_scripts/build_all.sh