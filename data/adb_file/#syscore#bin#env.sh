#!/bin/sh
export PREFIX=/syscore
export LD_LIBRARY_PATH=/syscore/lib/egl:/apex/com.android.art/lib64:/apex/com.android.os.statsd/lib64:/syscore/lib:/syscore/lib/weston:/syscore/lib/android
#export LD_LIBRARY_PATH=/system/lib64:/syscore/lib:/syscore/android/lib:/usr/lib:/lib:/usr/lib/pulseaudio/:$LD_LIBRARY_PATH
#export LD_LIBRARY_PATH=/mina/lib:/mina/android/lib:/usr/lib:/lib:/usr/lib/pulseaudio/:/system/lib64/:$LD_LIBRARY_PATH
#export LD_LIBRARY_PATH=/mina/lib:/usr/lib:/lib:/usr/lib/pulseaudio/:/system/lib64/:$LD_LIBRARY_PATH
export NODE_PATH=/syscore/lib/node_modules/
export SERVICE_MAIN_PATH=/syscore
export TMPDIR=/data_mirror/tmp
export PULSE_COOKIE="/data_mirror/run/pulse/.config/pulse/cookie"