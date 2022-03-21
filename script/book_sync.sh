_describe() { echo "nas备份腾讯云calibre书籍"; }
if [[ "${describe}" == "describe" ]];then _describe;exit 0;fi

rsync -avzu -e  'ssh -p 59422  -i /var/services/homes/hikhhbro/.ssh/hik-ssh/hikvps'   hik-vps@42.193.200.153:/data/calibre/books/  /volume2/bak/calibre_bak/books/