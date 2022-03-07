. base.sh

_task sed -i '/hik_run_complete.sh/d'  ~/.bashrc
_task sed -i '/HIK_SCRIPT_TOP_DIR/d'  ~/.bashrc
_task sudo rm  /usr/local/bin/hikrun
_task source ~/.bashrc