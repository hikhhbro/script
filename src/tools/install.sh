if [[ `which python3` == "" ]];then
  sudo apt-get install python3
fi
source ~/.bashrc

if [[ "${SCRIPT_TOP_DIR}" != "" ]] || [[ "${SCRIPT_TOOL_NAME}" != "" ]] ;then
    echo   "已安装过${SCRIPT_TOP_DIR} 正在卸载 .... "
    . src/tools/uninstall.sh  ${SCRIPT_TOOL_NAME}
fi


if [[ "$1" == "" ]];then
  read -p "请输入工具名称[hikrun]: " SCRIPT_TOOL_NAME
  if [[ "${SCRIPT_TOOL_NAME}" == "" ]];then
    SCRIPT_TOOL_NAME='hikrun'
  fi
else 
  SCRIPT_TOOL_NAME=$1
fi
if [[ "$2" == "" ]];then
   read -p "请输入工具安装路径[`pwd`]: " SCRIPT_TOP_DIR
  if [[ "${SCRIPT_TOP_DIR}" == "" ]];then
        SCRIPT_TOP_DIR=`pwd`
  fi
else 
  SCRIPT_TOP_DIR=$2
fi

if [[ "${SCRIPT_TOP_DIR}" != /* ]]; then
  SCRIPT_TOP_DIR="$(pwd)/${SCRIPT_TOP_DIR}"
fi
if command -v realpath >/dev/null 2>&1; then
  SCRIPT_TOP_DIR="$(realpath -m "${SCRIPT_TOP_DIR}")"
else
  SCRIPT_TOP_DIR="$(cd "$(dirname "${SCRIPT_TOP_DIR}")" && pwd)/$(basename "${SCRIPT_TOP_DIR}")"
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

init_tool_configs() {
  local template_dir="${SCRIPT_TOP_DIR}/src/template/config"
  if [[ ! -d "${template_dir}" ]]; then
    return
  fi
  local template name data_dir target
  for template in "${template_dir}"/*.json; do
    [[ -f "${template}" ]] || continue
    name="$(basename "${template}" .json)"
    data_dir="${SCRIPT_TOP_DIR}/data/${name}"
    target="${data_dir}/config.json"
    mkdir -p "${data_dir}"
    if [[ ! -s "${target}" ]] || [[ "$(tr -d '[:space:]' < "${target}")" == "{}" ]]; then
      cp "${template}" "${target}"
    fi
  done
}

init_tool_configs


sed -i '/SCRIPT_TOP_DIR/d'  ~/.bashrc
sed -i '/SCRIPT_TOOL_NAME/d'  ~/.bashrc

sed -i "/shopt -oq posix/iexport SCRIPT_TOP_DIR=\"${SCRIPT_TOP_DIR}\"" ~/.bashrc
sed -i "/shopt -oq posix/iexport SCRIPT_TOOL_NAME=\"${SCRIPT_TOOL_NAME}\"" ~/.bashrc
_task source ~/.bashrc

cat > "${SCRIPT_TOP_DIR}/${SCRIPT_TOOL_NAME}" <<EOF
#!/usr/bin/python3
import os
import sys
root_dir = os.getenv('SCRIPT_TOP_DIR')
sys.path.append(root_dir)
from src import main

if __name__ == '__main__':
    main.run()
EOF
_task sudo mv ${SCRIPT_TOP_DIR}/${SCRIPT_TOOL_NAME} /usr/local/bin/${SCRIPT_TOOL_NAME}
_task sudo chmod 755 /usr/local/bin/${SCRIPT_TOOL_NAME}

cat  >  "${SCRIPT_TOP_DIR}/${SCRIPT_TOOL_NAME}_prompt" <<EOF
if [[ -e ${SCRIPT_TOP_DIR}/src/completion/complete.sh ]]; then
	. ${SCRIPT_TOP_DIR}/src/completion/complete.sh
fi

${SCRIPT_TOOL_NAME}() {
	if [[ "\$1" == "note" && "\$2" == "cd" ]]; then
		local __hikrun_cd_cmd
		__hikrun_cd_cmd="\$(HIKRUN_PRINT_CD=1 command ${SCRIPT_TOOL_NAME} "\$@")" || return
		eval "\${__hikrun_cd_cmd}"
		return
	fi
	command ${SCRIPT_TOOL_NAME} "\$@"
}
EOF
_task sudo mv ${SCRIPT_TOP_DIR}/${SCRIPT_TOOL_NAME}_prompt /etc/bash_completion.d/${SCRIPT_TOOL_NAME}_prompt
_task sudo chmod 755 /etc/bash_completion.d/${SCRIPT_TOOL_NAME}_prompt
_task source ~/.bashrc
echo -n "---安装完成---输入任意键结束------"
read 
exit 0
