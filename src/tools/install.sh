. base.sh
if [[ `which python3` == "" ]];then
  sudo apt-get install python3
fi

if [[ "$1" == "" ]];then
  SCRIPT_TOOL_NAME='hikrun'
else 
  SCRIPT_TOOL_NAME=$1
fi


if [ -f "/usr/local/bin/${SCRIPT_TOOL_NAME}" ];then
echo "卸载"
. uninstall.sh
echo "卸载完成"
fi
if [ -f "/etc/bash_completion.d/${SCRIPT_TOOL_NAME}_prompt" ];then
echo "卸载"
. uninstall.sh
echo "卸载完成"
fi
echo "正在安装"

_task sed -i '/SCRIPT_TOP_DIR/d'  ~/.bashrc
echo "export SCRIPT_TOP_DIR=`pwd`" >> ~/.bashrc
_task source ~/.bashrc
_task sed -i '/SCRIPT_TOOL_NAME/d'  ~/.bashrc
echo "export SCRIPT_TOOL_NAME=${SCRIPT_TOOL_NAME}" >> ~/.bashrc
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

echo ". `pwd`/complete_prompt.sh \$*" >  ${SCRIPT_TOOL_NAME}_prompt
_task sudo mv ${SCRIPT_TOOL_NAME}_prompt /etc/bash_completion.d/${SCRIPT_TOOL_NAME}_prompt
_task sudo chmod 755 /etc/bash_completion.d/${SCRIPT_TOOL_NAME}_prompt
_task source ~/.bashrc
echo -n "---安装完成---输入任意键结束------"
read 
exit 0