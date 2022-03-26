. base.sh

_task sed -i '/HIK_SCRIPT_TOP_DIR/d'  ~/.bashrc
if [ -f "/usr/local/bin/hikrun" ];then
_task sudo rm  /usr/local/bin/hikrun
fi
if [ -f "/etc/bash_completion.d/hikrun_prompt" ];then
_task sudo rm /etc/bash_completion.d/hikrun_prompt
fi
if [ -f "/etc/bash_completion.d/z" ];then
_task sudo rm /etc/bash_completion.d/z
fi
source ~/.bashrc