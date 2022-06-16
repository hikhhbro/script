. src/tools/base.sh

if [[ "$1" != "" ]];then
    SCRIPT_TOOL_NAME=$1
else
  if [[ "${SCRIPT_TOOL_NAME}" == "" ]];then
    _task echo -n "环境异常,输入需要卸载的安装目录:"
    read tool_dir
    if [[ "${tool_dir}" == "" ]] || [[ ! -d ${tool_dir} ]];then
        echo ""
        echo "输入目录不存在"
        exit 1
    fi
    if [ "-f ${tool_dir}/src/completion/.bashrc" ];then
        source   ${tool_dir}/src/completion/.bashrc
    fi
  fi
fi
sed -i '/SCRIPT_TOP_DIR/d'  ~/.bashrc
sed -i '/SCRIPT_TOOL_NAME/d'  ~/.bashrc
_task sudo rm  /usr/local/bin/${SCRIPT_TOOL_NAME}
_task sudo rm /etc/bash_completion.d/${SCRIPT_TOOL_NAME}_prompt
source ~/.bashrc