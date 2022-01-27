#minabase
#y4
y4_minabase_build() {
  _func "未支持"
}
y4_minabase_download() {
  _func "repo init -u git@git.n.xiaomi.com:minabase/manifest.git -b mina -m amlogic.xml"
  repo init -u git@git.n.xiaomi.com:minabase/manifest.git -b mina -m amlogic.xml
  repo sync -j16
}
#安卓
android_minabase_build() {
  _func "未支持"
}
android_minabase_download() {
  _func "repo init -u git@git.n.xiaomi.com:minabase/manifest.git -b mina"
  repo init -u git@git.n.xiaomi.com:minabase/manifest.git -b mina
  repo sync -j16
}
#minacose
#android
android_minacore_build() {
  _func ${out_target[*]}
  _task ./build/build.py init out --target-cpu arm
  _task ./build/build.py build -C out $out_target
}
android_minacore_rootfs() {
  _func
  ./build/build.py rootfs -C out mina
}
android_minacore_download() {
  _func "git@git.n.xiaomi.com:minacore/manifest.git ${dev} -m android.xml"
  repo init -u git@git.n.xiaomi.com:minacore/manifest.git ${dev} -m android.xml
  repo sync -j16
}
android_minacore_prebuilt() {
  _func
  ./build/build.py prebuilt
}
#y4
y4_minacore_build() {
  _func ${out_target[*]}
  ./build/build.py init out --target-cpu arm
  ./build/build.py build -C out $out_target
}
y4_minacore_rootfs() {
  _func
  ./build/build.py rootfs -C out mina
}
y4_minacore_download() {
  _func "git@git.n.xiaomi.com:minacore/manifest.git ${dev} -m tvos.xml"
  repo init -u git@git.n.xiaomi.com:minacore/manifest.git ${dev} -m tvos.xml
  repo sync -j16
}
y4_minacore_prebuilt() {
  _func
  ./build/build.py prebuilt
}
#android
android_native_rootfs() {
  _func
  source build/envsetup.sh
  lunch venus-userdebug
  ./device/xiaomi/venus/flash_scripts/build_all.sh
}
android_native_build() {
  _func
  source build/envsetup.sh
  lunch venus-userdebug
  ./mibuild.sh dist -j20 | tee build_full.log
}
android_native_download() {
  _func
  repo init -u git@git.n.xiaomi.com:system_dev/android_mirror/mi-r11/manifests/bsp-venus-r.git -m  bsp-venus-r.xml
  repo sync -c -j16
}