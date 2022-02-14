rsync -avzu -e  'ssh -p 59422  -i /var/services/homes/hikhhbro/.ssh/hik-ssh/hikvps'   --exclude-from '/root/script/script/wiz/wiz_sync_exclude.list'  hik-vps@42.193.200.153:/home/hik-vps/wizdata/  /volume2/bak/wizdata_bak/
rsync -avzu -e  'ssh -p 59422  -i /var/services/homes/hikhhbro/.ssh/hik-ssh/hikvps' hik-vps@42.193.200.153:/home/hik-vps/wizdata_bak/  /volume2/bak/wizdata_bak/db/
chown root:root /volume2/bak/wizdata_bak/db/auto.cnf
chmod 640 /volume2/bak/wizdata_bak/db/auto.cnf       
chown root:root /volume2/bak/wizdata_bak/db/ibtmp1
chmod 640  /volume2/bak/wizdata_bak/db/ibtmp1         
