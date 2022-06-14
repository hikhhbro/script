if [[ `which python3` == "" ]];then
  sudo apt-get install python3
fi
source ~/.bashrc

if [[ "${SCRIPT_TOP_DIR}" != "" ]] || [[ "${SCRIPT_TOOL_NAME}" != "" ]] ;then
    echo   "已安装过${SCRIPT_TOP_DIR} 正在卸载 .... "
    . src/tools/uninstall.sh  ${SCRIPT_TOOL_NAME}
fi


if [[ "$1" == "" ]];then
  SCRIPT_TOOL_NAME='hikrun'
else 
  SCRIPT_TOOL_NAME=$1
fi
if [[ "$2" == "" ]];then
  SCRIPT_TOP_DIR=`pwd`
else 
  SCRIPT_TOP_DIR=$2
fi
. src/tools/base.sh

if [ -f "/usr/local/bin/${SCRIPT_TOOL_NAME}" ];then
echo "卸载"
. src/tools/uninstall.sh ${SCRIPT_TOOL_NAME}
echo "卸载完成"
fi
if [ -f "/etc/bash_completion.d/${SCRIPT_TOOL_NAME}_prompt" ];then
echo "卸载"
. src/tools/uninstall.sh ${SCRIPT_TOOL_NAME}
echo "卸载完成"
fi
echo "正在安装"


sed -i '/SCRIPT_TOP_DIR/d'  ~/.bashrc
sed -i '/SCRIPT_TOOL_NAME/d'  ~/.bashrc

sed -i "/shopt -oq posix/iexport SCRIPT_TOP_DIR=\"`pwd`\"" ~/.bashrc
sed -i "/shopt -oq posix/iexport SCRIPT_TOOL_NAME=\"`pwd`\"" ~/.bashrc
_task source ~/.bashrc

cat > ${SCRIPT_TOP_DIR}/${SCRIPT_TOOL_NAME} <<EOF
#!/usr/bin/python3
import os
import sys
root_dir = os.getenv('SCRIPT_TOP_DIR')
sys.path.append(root_dir)
from src import main

if __name__ == '__main__':
    main.main()
EOF
_task sudo mv ${SCRIPT_TOP_DIR}/${SCRIPT_TOOL_NAME} /usr/local/bin/${SCRIPT_TOOL_NAME}
_task sudo chmod 755 /usr/local/bin/${SCRIPT_TOOL_NAME}

echo  >  ${SCRIPT_TOOL_NAME}_prompt <<EOF
if [[ -e ${SCRIPT_TOP_DIR}/src/completion/complete.sh ]]; then
	. ${SCRIPT_TOP_DIR}/src/completion/complete.sh
fi
EOF
_task sudo mv ${SCRIPT_TOOL_NAME}_prompt /etc/bash_completion.d/${SCRIPT_TOOL_NAME}_prompt
_task sudo chmod 755 /etc/bash_completion.d/${SCRIPT_TOOL_NAME}_prompt
_task source ~/.bashrc
echo -n "---安装完成---输入任意键结束------"
read 
exit 0