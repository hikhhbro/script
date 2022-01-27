rsync -avzu -e  'ssh -p 59422  -i /var/services/homes/hik/.ssh/hikvps'   --exclude-from '/root/script/wiz_sync_exclude.list'  hik-vps@42.193.200.153:/home/hik-vps/wizdata/  /volume2/wizdata_bak/ -y

rsync -avzu -e  'ssh -p 59422  -i /var/services/homes/hik/.ssh/hikvps' hik-vps@42.193.200.153:/home/hik-vps/wizdata_bak/  /volume2/wizdata_bak/db/ -y

chown  root:root /volume2/wizdata_bak/db/auto.cnf
chown  root:root /volume2/wizdata_bak/db/ibtmp1
