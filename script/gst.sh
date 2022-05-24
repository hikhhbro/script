gst_dir=(gst-rtsp-server gst-plugins-ugly gst-libav gst-plugins-good gst-devtools gst-plugins-bad gstreamer gst-editing-services gst-plugins-base)

cd /home/hik/ws/core_work/minacore_mon/external
for i in ${gst_dir[*]}
do 
  cd  /home/hik/ws/core_work/minacore_mon/external/$i
  mkdir -p home/hik/ws/core_work/minacore_mon/.repo/manifests/products/mi11/$i
  cp /home/hik/ws/core_work/minacore_mon/external/$i/build.yaml home/hik/ws/core_work/minacore_mon/.repo/manifests/products/mi11/$i/
done