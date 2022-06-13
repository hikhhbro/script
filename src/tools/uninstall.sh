. base.sh

_task sed -i '/HIK_SCRIPT_TOP_DIR/d'  ~/.bashrc
_task sudo rm  /usr/local/bin/hikrun
_task sudo rm /etc/bash_completion.d/hikrun_prompt
source ~/.bashrc