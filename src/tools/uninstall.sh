. base.sh

if [[ "$1" != "" ]];then
    SCRIPT_TOOL_NAME=$1
fi

_task sed -i '/SCRIPT_TOP_DIR/d'  ~/.bashrc
_task sed -i '/SCRIPT_TOOL_NAME/d'  ~/.bashrc
_task sudo rm  /usr/local/bin/${SCRIPT_TOOL_NAME}
_task sudo rm /etc/bash_completion.d/${SCRIPT_TOOL_NAME}_prompt
source ~/.bashrc