log="/home/hik/.var/log/ip.log"
hik_lap_ip=`ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6 | grep -v 192.168|awk '{print $2}'|tr -d "addr:"​`
old_hik_lap_ip=`cat $log`
if [[ "$old_hik_lap_ip" != "$hik_lap_ip" ]];then
    echo $hik_lap_ip > $log
fi
