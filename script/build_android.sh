#!/bin/bash
source build/envsetup.sh
lunch venus-userdebug
./mibuild.sh dist -j20 | tee build_full.log
./device/xiaomi/venus/flash_scripts/build_all.sh